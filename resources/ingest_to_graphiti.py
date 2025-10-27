"""
ARIA Knowledge System - Graphiti Ingestion (Option B)
Ingests parsed reports into Graphiti for knowledge graph storage

Version: 1.5.0 - Anthropic Usage API Integration (Option A)
- Added metadata "description" field for agent tracking in Usage API
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import asyncio
import json
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from graphiti_core import Graphiti
from graphiti_core.llm_client import LLMConfig
from graphiti_core.llm_client.anthropic_client import AnthropicClient
import sentry_sdk
from sentry_sdk.integrations.anthropic import AnthropicIntegration

# Import Sentry config
scripts_dir = Path(__file__).parent.parent.parent / "scripts"
sys.path.insert(0, str(scripts_dir))
from sentry_config import init_sentry


class GraphitiIngestion:
    """Ingest reports into Graphiti knowledge graph using Claude Haiku 4.5."""
    
    def __init__(
        self,
        neo4j_uri: str = "bolt://localhost:7687",
        neo4j_user: str = "neo4j",
        neo4j_password: str = "aria_knowledge_2025",
        use_anthropic: bool = True  # NEW: Use Claude Haiku 4.5 by default
    ):
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.use_anthropic = use_anthropic
        self.graphiti: Optional[Graphiti] = None
        self._current_description: Optional[str] = None  # NEW: Track current agent description
        
    async def initialize(self):
        """Initialize Graphiti client with Claude Haiku 4.5 (async)."""
        if self.graphiti is None:
            # Configure LLM client with metadata support
            llm_client = None
            if self.use_anthropic:
                # Use Claude Haiku 4.5 for LLM operations
                anthropic_key = os.getenv('ANTHROPIC_API_KEY')
                if not anthropic_key:
                    raise ValueError("ANTHROPIC_API_KEY not found in environment")
                
                llm_config = LLMConfig(
                    api_key=anthropic_key,
                    model='claude-haiku-4-5-20251001'  # Haiku 4.5 official model ID
                )
                llm_client = AnthropicClient(config=llm_config, cache=False)
                
                # ⭐ MONKEY-PATCH: Inject metadata into Anthropic API calls
                self._patch_anthropic_client(llm_client)
                
                print("🤖 Using Claude Haiku 4.5 for LLM operations (v1.5.0)")
                print("📊 Anthropic Usage API tracking enabled (metadata injection)")
            else:
                print("🤖 Using OpenAI (default) for LLM operations")
            
            # Initialize Graphiti
            self.graphiti = Graphiti(
                self.neo4j_uri,
                self.neo4j_user,
                self.neo4j_password,
                llm_client=llm_client  # Pass Claude Haiku 4.5 client (or None for OpenAI default)
                # embedder remains default (OpenAI) - no alternative exists
            )
            print("✅ Graphiti initialized (LLM: Claude Haiku 4.5, Embeddings: OpenAI)")
    
    def _patch_anthropic_client(self, client: AnthropicClient):
        """
        Monkey-patch Anthropic client to inject metadata into API calls.
        
        This patches the `_generate_response` method to add metadata={"user_id": "AGENT-DATE"}
        to the Anthropic messages.create() call, enabling precise token tracking in Usage API.
        
        Note: We patch _generate_response (not generate_response) because that's where
        the actual client.messages.create() call happens.
        """
        original_generate_response = client._generate_response
        
        async def patched_generate_response(
            messages,
            response_model=None,
            max_tokens=None,
            model_size=None,
        ):
            # Store reference to original client.messages.create
            original_create = client.client.messages.create
            
            async def patched_create(*args, **kwargs):
                # Inject metadata if we have a current description
                if self._current_description:
                    # Anthropic API metadata format: {"user_id": "AGENT-DATE"}
                    kwargs['metadata'] = {
                        'user_id': self._current_description
                    }
                    print(f"   📊 Injected metadata: user_id='{self._current_description}'")
                
                return await original_create(*args, **kwargs)
            
            # Temporarily replace messages.create with patched version
            client.client.messages.create = patched_create
            
            try:
                # Call original _generate_response (which will use our patched messages.create)
                return await original_generate_response(
                    messages, response_model, max_tokens, model_size
                )
            finally:
                # Restore original messages.create
                client.client.messages.create = original_create
        
        client._generate_response = patched_generate_response
        print("✅ Anthropic client patched for metadata injection (_generate_response)")
    
    def _build_description_metadata(self, report_data: Dict[str, Any]) -> str:
        """
        Build description for Anthropic Usage API tracking.
        
        Format: "AGENT-NAME-YYYY-MM-DD"
        Example: "CARO-DAILY-2025-10-26"
        
        This description field will appear in Anthropic Usage API responses,
        allowing precise token attribution per agent per day.
        
        Args:
            report_data: Report data with agent, type, date
            
        Returns:
            Description string for Anthropic metadata
        """
        agent = report_data.get("agent", "UNKNOWN")
        date = report_data.get("date", datetime.now().strftime("%Y-%m-%d"))
        
        # Format: AGENT-YYYY-MM-DD
        description = f"{agent}-{date}"
        
        print(f"📊 Anthropic metadata description: {description}")
        return description
    
    async def add_episode(
        self, 
        report_data: Dict[str, Any], 
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Add a report as an episode to Graphiti with automatic retry on rate limit.
        
        Graphiti will automatically:
        - Extract entities (Person, Project, Organization, etc.)
        - Detect relationships between entities
        - Add temporal information (valid_at timestamps)
        - Store in Neo4j graph
        
        Args:
            report_data: Parsed report data
            max_retries: Maximum number of retry attempts on rate limit (default: 3)
            
        Returns:
            Dict with status, episode_id, entities_count, relations_count
            
        Raises:
            Exception: If ingestion fails after all retries
        """
        await self.initialize()
        
        episode_id = report_data["episode_id"]
        content = report_data["content"]
        timestamp = report_data["timestamp"]
        
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
        
        # Prepare episode metadata
        metadata = {
            "agent": report_data["agent"],
            "type": report_data["type"],
            "date": report_data["date"],
            "context": report_data.get("context", "unknown"),  # ⭐ NEW: Pro/Personal separation (v1.6.0)
        }
        
        # Add optional metadata fields if present
        if "metadata" in report_data:
            if "file_path" in report_data["metadata"]:
                metadata["source_file"] = report_data["metadata"]["file_path"]
            if "word_count" in report_data["metadata"]:
                metadata["word_count"] = report_data["metadata"]["word_count"]
        
        print(f"📤 Adding episode to Graphiti: {episode_id}")
        print(f"   Content length: {len(content)} chars")
        print(f"   Timestamp: {timestamp}")
        
        # Start Sentry transaction for monitoring
        with sentry_sdk.start_transaction(
            op="graphiti.add_episode",
            name=f"Ingest: {episode_id}"
        ) as transaction:
            # Add context tags
            sentry_sdk.set_tag("agent", report_data["agent"])
            sentry_sdk.set_tag("report_type", report_data["type"])
            sentry_sdk.set_tag("context", report_data.get("context", "unknown"))  # ⭐ NEW: Pro/Personal separation (v1.6.0)
            sentry_sdk.set_tag("episode_id", episode_id)
            sentry_sdk.set_tag("content_length", len(content))
            
            # Retry loop for rate limit handling
            for attempt in range(max_retries):
                try:
                    # Build description metadata for Anthropic Usage API tracking
                    description_tag = self._build_description_metadata(report_data)
                    
                    # Set current description for monkey-patched Anthropic client
                    self._current_description = description_tag
                    
                    # Add episode to Graphiti
                    # Graphiti will automatically extract entities and relationships
                    # The patched Anthropic client will inject metadata automatically
                    result = await self.graphiti.add_episode(
                        name=episode_id,
                        episode_body=content,
                        source_description=f"{report_data['agent']} {report_data['type']}",
                        reference_time=timestamp
                    )
                    
                    # Clear description after ingestion
                    self._current_description = None
                    
                    print(f"✅ Episode added to Graphiti")
                    
                    # Extract information from result
                    entities_count = 0
                    relations_count = 0
                    
                    if isinstance(result, dict):
                        entities_count = len(result.get('entities', []))
                        relations_count = len(result.get('relations', []))
                    
                    print(f"   Entities extracted: {entities_count}")
                    print(f"   Relations extracted: {relations_count}")
                    
                    # Add measurements to Sentry
                    sentry_sdk.set_measurement("entities_extracted", entities_count, "count")
                    sentry_sdk.set_measurement("relations_extracted", relations_count, "count")
                    sentry_sdk.set_tag("status", "success")
                    if attempt > 0:
                        sentry_sdk.set_tag("retries", attempt)
                    
                    return {
                        "status": "success",
                        "episode_id": episode_id,
                        "graphiti_result": result,
                        "entities_count": entities_count,
                        "relations_count": relations_count
                    }
                    
                except Exception as e:
                    error_msg = str(e).lower()
                    
                    # Check if this is a rate limit error
                    is_rate_limit = (
                        "rate limit" in error_msg or
                        "429" in error_msg or
                        "ratelimiterror" in error_msg
                    )
                    
                    if is_rate_limit and attempt < max_retries - 1:
                        # Calculate exponential backoff: 30s, 60s, 90s
                        wait_time = 30 * (attempt + 1)
                        
                        print(f"⏸️  Rate limit detected, waiting {wait_time}s before retry...")
                        print(f"   Attempt {attempt + 1}/{max_retries}")
                        
                        # Track retry in Sentry
                        sentry_sdk.set_tag("rate_limit_retry", attempt + 1)
                        sentry_sdk.set_tag("retry_wait_time", wait_time)
                        
                        await asyncio.sleep(wait_time)
                        continue  # Retry
                    
                    # Not a rate limit error, or last attempt failed
                    if is_rate_limit:
                        print(f"❌ Rate limit persists after {max_retries} attempts")
                        sentry_sdk.set_tag("status", "rate_limit_exhausted")
                    else:
                        print(f"❌ Error adding episode: {e}")
                        sentry_sdk.set_tag("status", "error")
                    
                    sentry_sdk.capture_exception(e)
                    raise
    
    async def search(
        self,
        query: str,
        num_results: int = 5,
        group_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search Graphiti knowledge graph.
        Combines vector similarity + graph context.
        """
        await self.initialize()
        
        results = await self.graphiti.search(
            query=query,
            num_results=num_results,
            group_ids=group_ids
        )
        
        return results
    
    async def close(self):
        """Close Graphiti client."""
        if self.graphiti:
            await self.graphiti.close()
            self.graphiti = None


# Sync wrapper for easier testing
class GraphitiIngestionSync:
    """Synchronous wrapper for GraphitiIngestion."""
    
    def __init__(self, *args, **kwargs):
        self.async_client = GraphitiIngestion(*args, **kwargs)
    
    def add_episode(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add episode (sync)."""
        return asyncio.run(self.async_client.add_episode(report_data))
    
    def search(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search (sync)."""
        return asyncio.run(self.async_client.search(query, num_results))
    
    def close(self):
        """Close client (sync)."""
        asyncio.run(self.async_client.close())


# Test function
async def main():
    """Test Graphiti ingestion with parsed report."""
    
    print("🧪 Graphiti Ingestion Test")
    print("=" * 50)
    print("")
    
    # Load parsed report
    test_data_path = Path("/Users/nicozefrench/Obsidian/.aria/knowledge/test_data/parsed_caro_report.json")
    
    if not test_data_path.exists():
        print("❌ No parsed report found. Run parser test first:")
        print("   .aria/knowledge/setup/06_test_parser.sh")
        return 1
    
    report_data = json.loads(test_data_path.read_text())
    
    print(f"📄 Loading report: {report_data['episode_id']}")
    print("")
    
    # Initialize Graphiti
    graphiti = GraphitiIngestion()
    
    try:
        # Add episode
        print("1. Adding episode to Graphiti...")
        result = await graphiti.add_episode(report_data)
        
        if result["status"] == "success":
            print("✅ Episode ingested successfully!")
        else:
            print("❌ Ingestion failed")
            return 1
        
        print("")
        
        # Test search
        print("2. Testing semantic search...")
        query = "What projects is Nicolas working on?"
        search_results = await graphiti.search(query, num_results=3)
        
        print(f"   Query: '{query}'")
        print(f"   Results: {len(search_results)}")
        
        if search_results:
            for i, result in enumerate(search_results, 1):
                # Handle different result formats
                if isinstance(result, dict):
                    content = result.get('content', result.get('name', 'N/A'))
                else:
                    content = str(result)
                print(f"   {i}. {content[:100]}...")
        else:
            print("   (No results yet - graph is being built)")
        
        print("")
        print("🎉 Graphiti ingestion test complete!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    finally:
        await graphiti.close()
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))

