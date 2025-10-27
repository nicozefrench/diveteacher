"""
ARIA Knowledge System - Nightly Ingestion (Option B)
Automatically ingests new reports into Graphiti

Version: 1.6.0 - K2000 Personal Reviews Integration + Pro/Personal Separation
"""

from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any
import asyncio
import json
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "ingestion"))

from parsers.caro_parser import CAROReportParser
from parsers.bob_parser import BobReportParser
from parsers.k2000_parser import K2000ReportParser  # NEW: Personal reviews
from parsers.steph_kb_parser import StephKBParser
from ingest_to_graphiti import GraphitiIngestion
from common.safe_queue import SafeIngestionQueue
import sentry_sdk

# Import Sentry config
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))
from sentry_config import init_sentry


class NightlyIngestion:
    """Nightly ingestion automation with rate limit protection."""
    
    def __init__(self, vault_path: str = "/Users/nicozefrench/Obsidian"):
        self.vault_path = Path(vault_path)
        self.caro_parser = CAROReportParser(vault_path)
        self.bob_parser = BobReportParser(vault_path)
        self.k2000_parser = K2000ReportParser(vault_path)  # NEW: Personal reviews
        self.steph_kb_parser = StephKBParser(vault_path)
        self.graphiti = GraphitiIngestion()
        self.safe_queue = SafeIngestionQueue()  # Rate limit protection
        self.log_path = Path("/Users/nicozefrench/Obsidian/logs/knowledge-ingestion")
        self.log_path.mkdir(parents=True, exist_ok=True)
        
    async def ingest_reports_since(self, days: int = 1) -> Dict[str, Any]:
        """
        Ingest all reports from the last N days.
        Default: 1 day (yesterday's reports)
        """
        # Start Sentry transaction for nightly ingestion
        with sentry_sdk.start_transaction(
            op="knowledge.nightly",
            name=f"Nightly Ingestion ({days} days)"
        ) as transaction:
            sentry_sdk.set_tag("days_back", days)
            sentry_sdk.set_tag("ingestion_type", "nightly_automation")
            
            results = {
                "timestamp": datetime.now().isoformat(),
                "days_back": days,
                "agents": {},
                "total_ingested": 0,
                "errors": []
            }
            
            # Daily ingestion: CARO (daily reviews) + BOB (status reports) + K2000 (personal reviews)
            # STEPH-KB is handled separately (snapshot-based, not date-filtered)
            agents = ["CARO", "BOB", "K2000"]  # NEW: Added K2000
            
            since_date = datetime.now() - timedelta(days=days)
            
            print(f"🔍 Looking for reports since {since_date.strftime('%Y-%m-%d')}")
            print("")
            
            try:
                # Initialize Graphiti
                await self.graphiti.initialize()
                
                for agent in agents:
                    print(f"Processing {agent} reports...")
                    agent_results = {
                        "reports_found": 0,
                        "reports_ingested": 0,
                        "errors": []
                    }
                    
                    with sentry_sdk.start_span(op="process_agent", description=f"Process {agent}"):
                        # Select appropriate parser and file pattern
                        if agent == "CARO":
                            parser = self.caro_parser
                            reports = parser.list_reports(agent, limit=10)
                            filename_pattern = "Review-Daily-"
                        elif agent == "BOB":
                            parser = self.bob_parser
                            reports = parser.list_reports(limit=10)
                            filename_pattern = "Status-Report-"
                        elif agent == "K2000":  # NEW: K2000 personal reviews
                            parser = self.k2000_parser
                            reports = parser.list_reports(limit=10)
                            filename_pattern = "Review-Daily-"  # Same pattern as CARO (different directory)
                        else:
                            print(f"  ⚠️  Unknown agent: {agent}")
                            continue
                        
                        if not reports:
                            print(f"  ℹ️  No {agent} reports found")
                            results["agents"][agent] = agent_results
                            continue
                        
                        for report_path in reports:
                            # Check if report is recent enough
                            # Extract date from filename
                            report_date_str = report_path.stem.replace(filename_pattern, "")
                            try:
                                report_date = datetime.strptime(report_date_str, "%Y-%m-%d")
                            except Exception as e:
                                print(f"  ⚠️  Could not parse date from {report_path.name}: {e}")
                                continue
                            
                            if report_date < since_date:
                                continue
                            
                            agent_results["reports_found"] += 1
                            
                            # Parse and ingest
                            try:
                                parsed = parser.parse_report(report_path)
                                
                                # Use safe queue to prevent rate limit bursts
                                await self.safe_queue.safe_ingest(self.graphiti, parsed)
                                
                                agent_results["reports_ingested"] += 1
                                print(f"  ✅ {report_path.name}")
                                    
                            except Exception as e:
                                error = f"{report_path.name}: {str(e)}"
                                agent_results["errors"].append(error)
                                results["errors"].append(error)
                                # Capture to Sentry
                                sentry_sdk.capture_exception(e)
                                print(f"  ❌ {report_path.name}: {e}")
                        
                        results["agents"][agent] = agent_results
                        results["total_ingested"] += agent_results["reports_ingested"]
                
                # Process STEPH Knowledge Base (change detection)
                print("")
                print("Processing STEPH Knowledge Base...")
                steph_kb_results = {
                    "snapshot_attempted": False,
                    "snapshot_ingested": False,
                    "skipped_unchanged": False,
                    "errors": []
                }
                
                with sentry_sdk.start_span(op="process_kb", description="Process STEPH KB"):
                    try:
                        # Check if KB has changed
                        if self.steph_kb_parser.has_changed_since_last_ingest():
                            steph_kb_results["snapshot_attempted"] = True
                            
                            # Parse KB
                            parsed_kb = self.steph_kb_parser.parse_knowledge_base()
                            
                            # Ingest snapshot using safe queue
                            await self.safe_queue.safe_ingest(self.graphiti, parsed_kb)
                            
                            # Mark as ingested
                            self.steph_kb_parser.mark_as_ingested()
                            
                            steph_kb_results["snapshot_ingested"] = True
                            results["total_ingested"] += 1
                            print(f"  ✅ Knowledge base snapshot ingested")
                        else:
                            steph_kb_results["skipped_unchanged"] = True
                            print(f"  ⏭️  Knowledge base unchanged, skipped")
                    
                    except Exception as e:
                        error = f"STEPH-KB: {str(e)}"
                        steph_kb_results["errors"].append(error)
                        results["errors"].append(error)
                        sentry_sdk.capture_exception(e)
                        print(f"  ❌ Error ingesting KB: {e}")
                
                results["agents"]["STEPH-KB"] = steph_kb_results
                
                print("")
                print(f"✅ Ingested {results['total_ingested']} reports")
                
                # Add Sentry measurements
                sentry_sdk.set_measurement("reports_ingested", results["total_ingested"], "count")
                sentry_sdk.set_measurement("errors_count", len(results["errors"]), "count")
                sentry_sdk.set_tag("status", "success" if not results["errors"] else "partial")
                
                # Save log
                log_file = self.log_path / f"ingestion-{datetime.now().strftime('%Y-%m-%d')}.json"
                log_file.write_text(json.dumps(results, indent=2))
                print(f"📝 Log saved to {log_file}")
                
                return results
                
            except Exception as e:
                # Capture fatal errors
                sentry_sdk.set_tag("status", "fatal_error")
                sentry_sdk.capture_exception(e)
                raise
    
    async def close(self):
        """Close connections."""
        await self.graphiti.close()


# CLI entrypoint
async def main():
    """Run nightly ingestion."""
    import sys
    
    # Initialize Sentry for nightly automation
    try:
        init_sentry(
            environment="nightly-automation-knowledge",
            release="aria-knowledge-v1.6.0"  # UPDATED: v1.6.0 with K2000
        )
        print("✅ Sentry monitoring initialized")
    except Exception as e:
        print(f"⚠️  Sentry initialization failed: {e}")
        print("   (Continuing without Sentry monitoring)")
    
    days_back = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    
    print("🌙 ARIA Knowledge System - Nightly Ingestion")
    print("=" * 50)
    print("")
    
    ingestion = NightlyIngestion()
    
    try:
        results = await ingestion.ingest_reports_since(days=days_back)
        
        print("")
        print("Summary:")
        for agent, agent_results in results["agents"].items():
            if agent == "STEPH-KB":
                # Special handling for KB
                if agent_results.get("snapshot_ingested"):
                    print(f"  {agent}: ✅ Snapshot ingested")
                elif agent_results.get("skipped_unchanged"):
                    print(f"  {agent}: ⏭️  Unchanged (skipped)")
                elif agent_results.get("errors"):
                    print(f"  {agent}: ❌ Error")
            else:
                # Regular agents
                print(f"  {agent}: {agent_results['reports_ingested']}/{agent_results['reports_found']} ingested")
        
        if results["errors"]:
            print("")
            print(f"⚠️  {len(results['errors'])} errors occurred")
            for error in results["errors"]:
                print(f"    - {error}")
            return 1
        
        print("")
        print("🎉 Nightly ingestion complete!")
        return 0
    
    except Exception as e:
        print(f"")
        print(f"❌ Fatal error: {e}")
        sentry_sdk.capture_exception(e)
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        await ingestion.close()


if __name__ == "__main__":
    exit(asyncio.run(main()))

