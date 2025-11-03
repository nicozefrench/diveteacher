# Guide de Migration : Architecture KAI (Knowledge AI Infrastructure)
## Structurer votre Personal AI Infrastructure avec Claude Code et Skills

---

## 📋 Table des matières

1. [Vue d'ensemble de l'architecture KAI](#vue-densemble)
2. [Philosophie et principes fondamentaux](#philosophie)
3. [Structure détaillée des répertoires](#structure-détaillée)
4. [Système de Context Management](#context-management)
5. [Intégration des Skills Anthropic](#skills-integration)
6. [Agents et orchestration](#agents-orchestration)
7. [Système d'enforcement multicouche](#enforcement-system)
8. [Plan de migration depuis Aria](#migration-plan)
9. [Exemples concrets et templates](#exemples-templates)
10. [Best practices et optimisations](#best-practices)

---

## 1. Vue d'ensemble de l'architecture KAI {#vue-densemble}

### Qu'est-ce que KAI ?

KAI (Knowledge AI Infrastructure) est une **architecture de Personal AI Infrastructure (PAI)** développée par Daniel Miessler qui transforme Claude Code en un assistant numérique puissant et contextuel. Le système repose sur trois piliers :

**🎯 Principe central : "Solve Once, Use Forever"**
- Chaque problème résolu devient un module réutilisable
- Architecture basée sur du texte/Markdown
- Context management distribué et hiérarchique
- Progressive disclosure du contexte

### Différences fondamentales avec une approche traditionnelle

| Approche traditionnelle | Architecture KAI |
|------------------------|------------------|
| CLAUDE.md monolithique | CLAUDE.md minimal pointant vers contexte distribué |
| Contexte global répété | Contexte chargé progressivement selon besoin |
| Instructions mélangées | Séparation claire: tools/agents/context/commands |
| Difficile à maintenir | Un seul endroit par type d'information |
| Context window saturé | Context window optimisé |

### Architecture en un coup d'œil

```
~/.claude/                          # Base de votre PAI
├── context/                        # 🧠 Le cerveau du système
│   ├── CLAUDE.md                   # Documentation maître UFC
│   ├── memory/                     # Mémoire système
│   ├── projects/                   # Contextes projets
│   ├── tools/                      # Documentation outils
│   ├── philosophy/                 # Principes & mental models
│   └── architecture/               # Design patterns
├── agents/                         # 🤖 Agents spécialisés
├── commands/                       # ⚡ Workflows custom
├── hooks/                          # 🪝 Automation événementielle
├── skills/                         # 🎓 Skills Anthropic
│   ├── public/                     # Skills Anthropic officiels
│   ├── user/                       # Vos skills custom
│   └── example/                    # Skills d'exemple
└── .mcp.json                       # Configuration MCP
```

---

## 2. Philosophie et principes fondamentaux {#philosophie}

### Principe #1 : Text as Thought Primitive

> "I consider text to be like a thought-primitive. A basic building block of life. A fundamental codex of thinking." - Daniel Miessler

**Application pratique :**
- Tout est en Markdown : instructions, configurations, contexte
- Les fichiers texte sont versionnables, auditables, composables
- Claude excelle avec du texte structuré

### Principe #2 : Progressive Context Disclosure

Ne chargez que le contexte nécessaire au moment nécessaire.

```
Niveau 1: Métadonnées (name, description) - Toujours en mémoire
   ↓
Niveau 2: Instructions principales - Chargées quand skill activé
   ↓
Niveau 3: Détails & exemples - Lus sur demande
   ↓
Niveau 4: Ressources externes - Chargées si nécessaire
```

### Principe #3 : System Design > Model Intelligence

> "The system, the orchestration, and the scaffolding are far more important than the model's intelligence."

**Conséquences :**
- 90% de la puissance vient d'un système bien conçu
- Un modèle moyen + bon système > modèle puissant + mauvais système
- Le système guide constamment le modèle avec le bon contexte

### Principe #4 : Solve Once, Modularize Forever

Chaque solution devient un module réutilisable :
- **Command** : Workflow spécifique (ex: `write-blog-post`)
- **Agent** : Spécialiste d'un domaine (ex: `engineer.md`)
- **Skill** : Capacité technique (ex: compétence PDF)
- **MCP Server** : API vers services externes

---

## 3. Structure détaillée des répertoires {#structure-détaillée}

### 3.1 Le répertoire `~/.claude/context/` - Le cerveau

C'est **LE** répertoire le plus important. Tout le savoir structuré de votre système y réside.

```
~/.claude/context/
├── CLAUDE.md                    # 📖 Master documentation
│                                #    Explique toute l'architecture
│
├── memory/                      # 🧠 Mémoire système
│   ├── learnings.md             #    Leçons apprises
│   ├── preferences.md           #    Préférences utilisateur
│   └── patterns.md              #    Patterns identifiés
│
├── projects/                    # 📁 Contextes par projet
│   ├── CLAUDE.md                #    Vue d'ensemble projets
│   ├── [project-name]/          #    Un dossier par projet
│   │   ├── CLAUDE.md            #    Config projet
│   │   ├── architecture.md      #    Architecture technique
│   │   ├── content/             #    Si projet contenu
│   │   │   └── CLAUDE.md        #    Standards écriture
│   │   └── troubleshooting/     #    Debug spécifique
│   │       └── CLAUDE.md
│   │
│   ├── ul-analytics/            #    Exemple : projet analytics
│   │   └── CLAUDE.md
│   └── website/                 #    Exemple : site web
│       ├── CLAUDE.md
│       ├── content/
│       │   └── CLAUDE.md
│       └── troubleshooting/
│           └── CLAUDE.md
│
├── tools/                       # 🔧 Documentation outils
│   ├── CLAUDE.md                #    Hub central des outils
│   ├── commands/                #    Documentation commands
│   │   └── CLAUDE.md
│   ├── mcp/                     #    Documentation MCP servers
│   │   └── CLAUDE.md
│   └── pai/                     #    Services PAI
│       └── CLAUDE.md
│
├── methodology/                 # 📊 Approches structurées
│   ├── perform-web-assessment/
│   ├── perform-company-recon/
│   └── tdd-workflow.md
│
├── philosophy/                  # 💭 Croyances fondamentales
│   ├── core-beliefs.md
│   ├── design-preferences/
│   │   └── ui-ux-principles.md
│   └── values.md
│
├── architecture/                # 🏗️ Design patterns système
│   ├── principles.md
│   ├── system-design.md
│   └── test-driven-development.md
│
├── development/                 # 💻 Philosophie dev
│   └── CLAUDE.md
│
├── documentation/               # 📝 Standards documentation
│   └── standards.md
│
├── testing/                     # 🧪 Stratégies de test
│   ├── testing-guidelines.md
│   ├── playwright-config.md
│   └── tdd-guide.md
│
├── troubleshooting/             # 🔍 Stratégies debug
│   └── CLAUDE.md
│
└── working/                     # 📝 Mémoire de travail active
    ├── CLAUDE.md                #    Protocole working memory
    ├── active/                  #    Tâches en cours
    │   └── [task-name]/         #    Une tâche = un dossier
    └── archive/                 #    Tâches complétées
```

### 3.2 Le fichier `CLAUDE.md` maître de contexte

**Emplacement** : `~/.claude/context/CLAUDE.md`

Ce fichier explique toute votre architecture de contexte. Exemple de structure :

```markdown
# KAI Context System - Master Documentation

## Architecture Overview

This document explains the complete context management system for KAI.
All knowledge is organized hierarchically in `~/.claude/context/`.

## Directory Structure

### 1. Projects (`projects/`)
Project-specific configurations and context. Each project has:
- Main CLAUDE.md with project overview
- Subdirectories for specific aspects (content, troubleshooting, etc.)

### 2. Tools (`tools/`)
Complete documentation of all available tools:
- Commands: Custom workflows
- MCP Servers: External integrations
- PAI Services: Personal API services

### 3. Memory (`memory/`)
System learnings and user preferences that persist across sessions.

### 4. Philosophy (`philosophy/`)
Core beliefs, principles, and mental models that guide all decisions.

[... continue avec chaque section ...]

## How This System Works

1. Minimal CLAUDE.md in project roots point here
2. Context is loaded progressively as needed
3. Never duplicate information - always reference
4. One source of truth for each piece of knowledge
```

### 3.3 Le répertoire `~/.claude/agents/`

Les agents sont des **personas spécialisées** avec expertise contextuelle.

```
~/.claude/agents/
├── engineer.md              # Développeur TypeScript/Bun
├── writer.md                # Rédacteur de contenu
├── pentester.md             # Expert sécurité
├── designer.md              # Designer UI/UX
├── marketer.md              # Marketing & copy
├── gamedesigner.md          # Mécanique RPG
├── qatester.md              # QA & testing
└── researcher.md            # Recherche & analyse
```

**Structure type d'un agent** (`engineer.md`) :

```markdown
---
name: Software Engineer
role: TypeScript/Bun Development Specialist
expertise: [typescript, bun, react, testing, architecture]
---

# Engineer Agent

You are an expert software engineer specializing in modern TypeScript
development with Bun runtime.

## Core Responsibilities

1. Write clean, type-safe TypeScript code
2. Follow TDD principles (read ~/.claude/context/testing/tdd-guide.md)
3. Ensure proper error handling
4. Optimize for performance

## Context to Load

ALWAYS read these before starting:
- ~/.claude/context/architecture/principles.md
- ~/.claude/context/testing/testing-guidelines.md
- ~/.claude/context/tools/CLAUDE.md (for available tools)

## Workflow

1. Understand requirements
2. Read relevant context files
3. Plan implementation
4. Write tests first
5. Implement solution
6. Verify & commit

## Code Style

[... preferences de code ...]

## Tools Available

Check ~/.claude/context/tools/CLAUDE.md for:
- MCP servers you can use
- Commands available
- Testing frameworks configured
```

### 3.4 Le répertoire `~/.claude/commands/`

Les commands sont des **workflows automatisés** pour tâches répétitives.

```
~/.claude/commands/
├── write-blog-post.md           # Génération d'article blog
├── create-custom-image.md       # Génération d'image AI
├── code-review.md               # Revue de code automatique
├── analyze-paper.md             # Analyse paper académique
├── create-d3-visualization.md   # Visualisations interactives
├── youtube-to-blog.md           # Conversion vidéo → article
└── add-links.md                 # Enrichissement de contenu
```

**Structure type d'une command** (`write-blog-post.md`) :

```markdown
# Write Blog Post Command

## Purpose
Transforms dictated or rough notes into a fully formatted blog post
following my writing standards.

## Usage
```bash
# From Claude Code
/command write-blog-post <input-file>

# Or just ask:
"Use the write-blog-post command on my notes about AI"
```

## Process

1. Read input content
2. Load writing standards from ~/.claude/context/projects/website/content/CLAUDE.md
3. Structure the content:
   - Engaging title
   - Clear introduction
   - Logical sections
   - Strong conclusion
4. Apply style guide:
   - Tone: [your preferences]
   - Length: [target word count]
   - Format: [Markdown specifics]
5. Generate header image using create-custom-image command
6. Output final formatted post

## Output Location
`~/projects/website/content/[slug].md`

## Dependencies
- create-custom-image command (for header)
- Writing style guide (in context/projects/website/content/)
```

### 3.5 Le répertoire `~/.claude/hooks/`

Les hooks sont des **scripts d'automation événementielle** qui s'exécutent à des moments clés.

```
~/.claude/hooks/
├── user-prompt-submit-context-loader.ts    # Avant chaque prompt
├── agent-complete.sh                       # Après agent terminé
├── subagent-complete.sh                    # Après sous-agent terminé
├── file-modified.ts                        # Après modification fichier
└── session-start.ts                        # Au démarrage session
```

**Exemple critique** : `user-prompt-submit-context-loader.ts`

```typescript
/**
 * Hook: user-prompt-submit
 * 
 * S'exécute AVANT chaque prompt utilisateur pour injecter
 * des instructions de chargement de contexte.
 * 
 * C'est le premier niveau du système d'enforcement.
 */

export default function onUserPromptSubmit(userMessage: string): string {
  const contextInstructions = `
// ⚠️ MANDATORY CONTEXT CHECK - READ THIS FIRST ⚠️
// You MUST load these context files before responding:
//
// 1. Read ~/.claude/context/CLAUDE.md (master context system)
// 2. Read ~/.claude/context/tools/CLAUDE.md (available tools)
// 3. Read ~/.claude/context/projects/CLAUDE.md (active projects)
//
// You will provide incorrect responses without this context.
// DO NOT skip this step. DO NOT lie about reading these files.
//
// Use the Read tool to actually load each file, then proceed.
//
// ============ USER'S ACTUAL MESSAGE BELOW ============

${userMessage}
`;

  return contextInstructions;
}
```

Ce hook est **crucial** : il force Claude à charger le contexte approprié avant chaque réponse.

### 3.6 Le répertoire `~/.claude/skills/` - Intégration Skills Anthropic

Les Skills sont la nouvelle façon d'étendre Claude avec des capacités techniques.

```
~/.claude/skills/
├── public/                      # Skills officiels Anthropic
│   ├── docx/
│   │   ├── SKILL.md             # Manipulation Word documents
│   │   └── [scripts & resources]
│   ├── xlsx/
│   │   ├── SKILL.md             # Manipulation Excel
│   │   └── [scripts & resources]
│   ├── pptx/
│   │   ├── SKILL.md             # Création PowerPoint
│   │   └── [scripts & resources]
│   ├── pdf/
│   │   ├── SKILL.md             # Manipulation PDF
│   │   └── forms.md
│   └── skill-creator/
│       └── SKILL.md             # Meta-skill pour créer skills
│
├── user/                        # Vos skills custom
│   ├── my-workflow/
│   │   ├── SKILL.md
│   │   └── scripts/
│   └── domain-expertise/
│       └── SKILL.md
│
└── example/                     # Skills d'exemple
    └── template-skill/
        └── SKILL.md
```

---

## 4. Système de Context Management {#context-management}

### 4.1 Le principe du CLAUDE.md minimal

Au lieu d'avoir un fichier CLAUDE.md gigantesque à la racine de chaque projet, utilisez un **pointeur minimal** :

**Exemple** : `~/projects/website/CLAUDE.md`

```markdown
# Website Project (~/projects/website/)

# 🚨 MANDATORY COMPLIANCE PROTOCOL 🚨

**FAILURE TO FOLLOW THESE INSTRUCTIONS = CRITICAL FAILURE**

## YOU MUST ALWAYS:

1. **READ ALL REFERENCED CONTEXT** - Every "See:" reference is MANDATORY

## Basic Configuration

LEARN this information about the website project:
→ See: ~/.claude/context/projects/website/CLAUDE.md

## Content Creation

LEARN how to create content for the site:
→ See: ~/.claude/context/projects/website/content/CLAUDE.md

## Troubleshooting

How to troubleshoot issues on the site:
→ See: ~/.claude/context/projects/website/troubleshooting/CLAUDE.md

## Required Actions

### YOU MUST USE AGENTS FOR ALL WORK

- For all writing tasks:
  → Use agent: ~/.claude/agents/writer.md

- For all development and troubleshooting:
  → Use agent: ~/.claude/agents/engineer.md

### NEVER proceed without loading the referenced contexts above
```

**Avantages de cette approche :**

✅ **Un seul endroit** à maintenir pour chaque type d'info
✅ **Pas de duplication** de contexte entre projets
✅ **Context window optimisé** - chargement à la demande
✅ **Évolutif** - ajoutez des contextes sans modifier les CLAUDE.md projets
✅ **Clair** - structure visible d'un coup d'œil

### 4.2 Structure d'un fichier de contexte

**Template** : `~/.claude/context/projects/[project]/CLAUDE.md`

```markdown
# [Project Name] - Context Configuration

## Overview

Brief description of the project, its purpose, and key characteristics.

## Architecture

### Tech Stack
- Frontend: [technologies]
- Backend: [technologies]
- Database: [technologies]
- Deployment: [platform]

### Key Dependencies
List important dependencies that affect how Claude should work.

## Development Guidelines

### Code Style
Preferences for this project (or reference to global standards).

### Testing Requirements
- Unit tests: [framework]
- Integration tests: [approach]
- E2E tests: [tool]

Reference: ~/.claude/context/testing/testing-guidelines.md

## Specific Context

### Business Logic
Explain domain-specific business rules Claude needs to understand.

### Known Issues / Gotchas
Document tricky parts or non-obvious behaviors.

### Common Tasks
List frequent operations with examples:
- "Fix build error" → [typical approach]
- "Add new feature" → [typical steps]

## Related Contexts

- Architecture: ~/.claude/context/architecture/system-design.md
- Testing: ~/.claude/context/testing/tdd-guide.md
- Tools: ~/.claude/context/tools/CLAUDE.md

## Agents to Use

- Development: ~/.claude/agents/engineer.md
- Design: ~/.claude/agents/designer.md
```

### 4.3 Le fichier `tools/CLAUDE.md` - Hub des outils

**Emplacement** : `~/.claude/context/tools/CLAUDE.md`

Ce fichier **central** documente tous vos outils et leur utilisation.

```markdown
# Tools Hub - Complete Documentation

## Overview

This file documents ALL tools available to KAI:
- Commands (custom workflows)
- MCP Servers (external integrations)
- Skills (technical capabilities)
- Fabric patterns (problem-solving templates)

## 1. Commands

Custom workflows for specific tasks.

### Available Commands

#### `write-blog-post`
**Purpose**: Transform notes into formatted blog posts
**Usage**: `/command write-blog-post <input>`
**Documentation**: ~/.claude/commands/write-blog-post.md

#### `create-custom-image`
**Purpose**: Generate contextual images using AI
**Usage**: `/command create-custom-image <context>`
**Documentation**: ~/.claude/commands/create-custom-image.md

[... list all commands ...]

## 2. MCP Servers

External service integrations via Model Context Protocol.

### Configuration File
`~/.claude/.mcp.json`

### Available MCP Servers

#### `playwright`
**Type**: Local executable
**Purpose**: Browser automation and web scraping
**Usage**: Automatically available for web interaction tasks

#### `httpx`
**Type**: HTTP API (Cloudflare Worker)
**Purpose**: Web server reconnaissance and stack detection
**Usage**: "Check the tech stack of example.com"
**API Key**: Required (configured in .mcp.json)

#### `content`
**Type**: HTTP API
**Purpose**: Access to all blog content and opinions archive
**Usage**: "Find my posts about AI security"

#### `daemon`
**Type**: HTTP API  
**Purpose**: Personal API for life data
**Usage**: "What was in my last meeting about X?"

[... document all MCP servers ...]

### MCP Usage Guidelines

1. **For web research**: Use `playwright` for scraping, `httpx` for reconnaissance
2. **For personal data**: Use `daemon` or `content` MCP
3. **For ports/security**: Use `naabu` MCP
4. **Always check MCP availability** before assuming functionality

## 3. Skills

Technical capabilities via Anthropic Skills system.

### Skills Location
`~/.claude/skills/`

### Available Skills

#### Document Skills (Public)

**docx** - Word document manipulation
- Create, edit, analyze .docx files
- Support for tracked changes, comments
- Auto-loaded when working with Word docs

**xlsx** - Excel spreadsheet handling
- Create sheets with formulas
- Data analysis and visualization
- Auto-loaded for spreadsheet tasks

**pptx** - PowerPoint presentations
- Create professional presentations
- Support for layouts, themes
- Auto-loaded for presentation work

**pdf** - PDF manipulation
- Extract text and tables
- Fill PDF forms
- Merge/split documents
- Auto-loaded for PDF tasks

[... document other skills ...]

### When Skills Are Used

Skills are **automatically invoked** by Claude based on task type.
You don't manually select them - Claude recognizes when needed.

## 4. Fabric Patterns

Problem-solving templates from the Fabric project.

### What is Fabric?

Fabric is a collection of 300+ prompts/patterns for common problems.

### Usage

```bash
# List available patterns
fabric -l

# Use a pattern
fabric -p [pattern-name]

# Web scraping with Jina
fabric -u <URL>
```

### Common Patterns

- `extract_wisdom`: Extract insights from content
- `create_summary`: Summarize long text
- `explain_code`: Understand code structure
- `analyze_claims`: Fact-check claims
- `improve_writing`: Enhance text quality

[... list key patterns ...]

## 5. Tool Orchestration

### How to Chain Tools

Many powerful workflows come from **chaining tools together**:

**Example 1: Security Assessment**
```
1. Use httpx MCP → detect tech stack
2. Use naabu MCP → scan ports
3. Use Fabric pattern (analyze_threats) → analyze results
4. Use write-blog-post command → document findings
```

**Example 2: Content Creation**
```
1. Use daemon MCP → fetch meeting notes
2. Use Fabric pattern (extract_wisdom) → key insights
3. Use write-blog-post command → create article
4. Use create-custom-image command → generate header
5. Output to website project
```

### Tool Selection Guidelines

**For research**: Web search → playwright → content MCP
**For development**: Read code → engineer agent → testing tools
**For content**: Note sources → writer agent → commands
**For security**: httpx → naabu → pentester agent → report

## 6. Tool Descriptions Best Practices

Write clear, specific descriptions for custom tools:

❌ Bad: "Helpful utility for files"
✅ Good: "Extracts text from PDFs and converts to Markdown format"

❌ Bad: "Does stuff with APIs"  
✅ Good: "Fetches GitHub repository metadata via REST API"

Clear descriptions help agents/subagents choose the right tool.

## Tool Maintenance

- Keep this file updated as tools evolve
- Document new MCP servers immediately
- Add usage examples for complex tools
- Remove deprecated tools
```

---

## 5. Intégration des Skills Anthropic {#skills-integration}

### 5.1 Qu'est-ce qu'un Skill ?

Un **Skill** est un module d'expertise technique que vous créez pour Claude :

- **Format** : Dossier contenant `SKILL.md` + ressources
- **Contenu** : Instructions + scripts + documentation
- **Activation** : Automatique quand la tâche le requiert
- **Localisation** : `~/.claude/skills/` ou `.claude/skills/` (projet)

### 5.2 Structure d'un Skill

**Template** : `~/.claude/skills/user/my-skill/SKILL.md`

```markdown
---
name: my-skill-name
description: Clear description of what this skill does and when to use it
license: MIT
metadata:
  version: "1.0.0"
  author: "Your Name"
  tags: ["category1", "category2"]
---

# My Skill Name

Comprehensive instructions that Claude will follow when this skill is active.

## When to Use This Skill

This skill should be used when:
- [Specific trigger condition 1]
- [Specific trigger condition 2]
- [Specific trigger condition 3]

## Core Capabilities

1. **Capability 1**: [Description]
2. **Capability 2**: [Description]
3. **Capability 3**: [Description]

## Prerequisites

Before using this skill, ensure:
- [Requirement 1]
- [Required tool/library]
- [Environment setup needed]

## Instructions

### Step 1: [Action Name]

[Detailed instructions for first step]

```bash
# Example command if applicable
example-command --flag value
```

### Step 2: [Action Name]

[Continue with numbered steps...]

## Examples

### Example 1: [Use Case]

**Task**: [Description of task]

**Approach**:
1. [Step 1]
2. [Step 2]
3. [Result]

**Code**:
```language
example code here
```

### Example 2: [Another Use Case]

[Similar structure...]

## Guidelines

- **Guideline 1**: [Important rule to follow]
- **Guideline 2**: [Best practice]
- **Guideline 3**: [Common pitfall to avoid]

## Error Handling

### Common Errors

**Error**: [Error message or condition]
**Cause**: [Why this happens]
**Solution**: [How to fix]

## Advanced Usage

[Optional advanced techniques or combinations]

## Related Resources

- Related skill: [`other-skill-name`]
- External docs: [URL]
- Related context: `~/.claude/context/[relevant-file].md`

## Testing This Skill

To verify this skill works:
1. [Test case 1]
2. [Expected result]
3. [How to confirm]
```

### 5.3 Progressive Disclosure dans les Skills

Le principe clé : **charger l'information par couches**.

**Niveau 1 - Métadonnées (toujours en mémoire)** :
```yaml
---
name: pdf-forms
description: Fill and extract data from PDF forms
---
```

**Niveau 2 - Instructions principales** :
```markdown
# PDF Forms Skill

Use this skill to:
- Read form fields from PDFs
- Fill PDF forms programmatically
- Extract data from filled forms

[Core instructions here...]
```

**Niveau 3 - Détails approfondis** :
```markdown
## Advanced: Handling Complex Forms

For forms with nested fields or special encoding...
[Detailed technical info...]
```

**Niveau 4 - Ressources externes** :
```markdown
## Reference

See `forms-api-docs.md` for complete API reference.
See `examples/complex-form.pdf` for test case.
```

### 5.4 Créer un Skill avec le skill-creator

Le `skill-creator` est un **meta-skill** qui vous aide à créer d'autres skills.

**Utilisation** :

```
// Dans Claude.ai ou Claude Code

"I want to create a skill for [specific workflow].
Can you help me using the skill-creator skill?"
```

Le skill-creator va :
1. Vous poser des questions sur votre workflow
2. Générer la structure de dossier appropriée
3. Formater le fichier SKILL.md
4. Suggérer les ressources nécessaires

**Exemple de conversation** :

```
You: I want to create a skill for analyzing Python codebases and 
     generating architecture diagrams.

Claude: [Using skill-creator]

I'll help you create a skill for Python codebase analysis and 
architecture diagram generation. Let me ask a few questions:

1. What Python analysis tools do you prefer? (e.g., ast, radon, pylint)
2. What diagram format should be output? (e.g., Mermaid, PlantUML, GraphViz)
3. What should trigger this skill? (specific file patterns, commands?)
4. Any specific architectural patterns to detect? (MVC, microservices, etc.)

[After answers, generates complete skill structure...]
```

### 5.5 Où placer vos Skills dans l'architecture KAI

**Option 1 : Skills globaux (disponibles partout)**
```
~/.claude/skills/user/[skill-name]/
└── SKILL.md
```

**Option 2 : Skills spécifiques à un projet**
```
~/projects/[project-name]/.claude/skills/[skill-name]/
└── SKILL.md
```

**Option 3 : Via plugin marketplace**
```bash
# Dans Claude Code
/plugin install [skill-name]@[marketplace]
```

**Recommandation KAI** :
- Skills **génériques/réutilisables** → `~/.claude/skills/user/`
- Skills **spécifiques projet** → `[project]/.claude/skills/`
- Skills **officiels** → `~/.claude/skills/public/` (via plugins)

### 5.6 Intégration Skills ↔ Context System

Les Skills **complètent** le context system, ils ne le remplacent pas :

| Context System | Skills |
|----------------|--------|
| Instructions générales | Capacités techniques spécifiques |
| Principes & philosophie | Exécution de code & manipulation fichiers |
| Références entre contextes | Opérations autonomes |
| Orchestration high-level | Actions low-level |

**Exemple d'intégration** :

```markdown
# Dans ~/.claude/context/projects/website/content/CLAUDE.md

## Content Creation Process

1. Load content standards (this file)
2. Use writer agent (~/.claude/agents/writer.md)
3. **Use docx skill** for Word document creation
4. **Use create-custom-image command** for header
5. Apply style guide from this context

## Skills Available for This Project

- **docx**: For creating formatted articles
- **custom-image-gen**: For blog headers
- **seo-optimizer**: Custom skill for SEO checks
  Location: ./.claude/skills/seo-optimizer/
```

### 5.7 Référencer des Skills depuis le Context

**Dans vos fichiers de contexte**, documentez les skills pertinents :

```markdown
# ~/.claude/context/tools/CLAUDE.md

## Skills Integration

### Document Creation Skills

When working with documents, these skills are available:

**docx** (public skill)
- Use for Word document creation and editing
- Auto-activated when .docx files are mentioned
- Advanced features: tracked changes, comments, styles

**pdf** (public skill)  
- Use for PDF manipulation and form filling
- Auto-activated for PDF tasks
- Can extract tables, text, fill forms

**custom-report-generator** (user skill)
- Location: ~/.claude/skills/user/custom-report-generator/
- Use for creating company-specific reports
- Combines docx skill + company templates
- Trigger: "Generate quarterly report"
```

---

## 6. Agents et orchestration {#agents-orchestration}

### 6.1 Philosophie des Agents

Les agents sont des **personas spécialisées** qui :
- Ont une expertise de domaine
- Chargent un contexte spécifique
- Suivent des workflows définis
- Peuvent appeler d'autres agents (sub-agents)

### 6.2 Créer un Agent efficace

**Template** : `~/.claude/agents/[agent-name].md`

```markdown
---
name: [Agent Name]
role: [Specific Role]
expertise: [list, of, areas]
priority: high | medium | low
---

# [Agent Name]

## Identity

You are [persona description]. Your expertise includes [domain knowledge].

## Core Mission

[What this agent is fundamentally responsible for]

## Context Loading Protocol

### MANDATORY - Load Before ANY Action

1. **System Context**
   - Read: ~/.claude/context/CLAUDE.md (understand system architecture)
   - Read: ~/.claude/context/tools/CLAUDE.md (know available tools)

2. **Domain Context**
   - Read: ~/.claude/context/[relevant-domain]/
   - Read: [any other relevant contexts]

3. **Project Context (if applicable)**
   - Read: ~/.claude/context/projects/[current-project]/CLAUDE.md

### Verification

After loading context, verify you understand:
- Available tools and how to use them
- Project-specific requirements
- Your role boundaries

## Responsibilities

### Primary Tasks
1. [Task 1 with details]
2. [Task 2 with details]
3. [Task 3 with details]

### Secondary Tasks
- [Supporting task 1]
- [Supporting task 2]

## Workflow

### Standard Operating Procedure

1. **Understand** → Clarify requirements
2. **Research** → Load relevant context
3. **Plan** → Create implementation plan
4. **Execute** → Perform work
5. **Verify** → Test results
6. **Document** → Update relevant files

### Decision Tree

```
User Request
    ↓
Does this match my expertise? 
    ├─ Yes → Proceed with workflow
    ├─ Partial → Collaborate with [other agent]
    └─ No → Delegate to [appropriate agent]
```

## Tools & Skills

### Preferred Tools
- [Tool 1]: Use for [purpose]
- [Tool 2]: Use for [purpose]
- [MCP Server 1]: For [integration]

### Skills to Leverage
- [Skill 1]: When [condition]
- [Skill 2]: For [use case]

### Commands Available
```bash
/command [command-name]  # [Purpose]
```

## Collaboration

### When to Call Sub-Agents

- **For [specific task]** → Call [sub-agent-name]
  Handoff: "Pass context X and Y"

- **For [another task]** → Call [another-agent]
  Handoff: "Provide Z, expect output in format Q"

### Communication Protocol

When collaborating:
1. Provide clear context handoff
2. Specify expected output format
3. Include relevant file paths
4. Document decision rationale

## Quality Standards

### Code Quality (if applicable)
- [Standard 1]
- [Standard 2]
- Reference: ~/.claude/context/architecture/principles.md

### Documentation Requirements
- [What to document]
- [Documentation format]
- [Where to place docs]

### Testing Requirements
- [Test coverage expectation]
- [Testing approach]
- Reference: ~/.claude/context/testing/testing-guidelines.md

## Error Handling

### When Things Go Wrong

1. **Read error carefully**
2. **Check context** - Did you load all required files?
3. **Review tools** - Are you using the right tool for the job?
4. **Consult troubleshooting** - See ~/.claude/context/troubleshooting/
5. **Ask for help** - If stuck, surface the issue clearly

## Limitations

### Things This Agent Does NOT Do
- [Out of scope task 1]
- [Out of scope task 2]
→ Refer these to [appropriate agent]

## Examples

### Example 1: [Common Task]

**Input**: [Example request]

**Process**:
1. Load context: [specific files]
2. Use tool: [tool name]
3. Execute: [steps]
4. Output: [result format]

**Example Transcript**:
```
User: [example request]
Agent: [step-by-step response]
```

### Example 2: [Complex Task]

[Similar structure...]

## Continuous Improvement

### Learning Points
- Track common issues in ~/.claude/context/memory/learnings.md
- Update agent definition as patterns emerge
- Refine context loading based on actual needs

## Agent Metadata

- **Version**: 1.0
- **Last Updated**: [Date]
- **Maintained By**: [Maintainer]
- **Related Agents**: [list of complementary agents]
```

### 6.3 Pattern d'Orchestration Multi-Agents

**Exemple : Création d'un feature complet**

```
User Request: "Build a user authentication system"
    ↓
Main Agent (Engineer)
    ├─ Loads context (architecture, security, testing)
    ├─ Creates implementation plan
    ├─ Calls Security Agent → Security review of plan
    ├─ Calls Database Agent → Schema design
    ├─ Implements core logic
    ├─ Calls Test Agent → Write test suite
    └─ Documents & commits

Flow:
1. Engineer agent receives request
2. Loads security + architecture contexts
3. Plans implementation
4. Delegates security audit to Pentester agent
5. Pentester returns security requirements
6. Engineer implements with requirements
7. Delegates testing to QA agent
8. QA agent validates implementation
9. Engineer commits and documents
```

### 6.4 Agents vs Commands vs Skills

| Type | Purpose | When to Use |
|------|---------|-------------|
| **Agent** | Specialized persona with domain expertise | Complex tasks requiring judgment & context |
| **Command** | Automated workflow for specific task | Repetitive, well-defined processes |
| **Skill** | Technical capability (code execution) | File manipulation, data processing |

**Exemple de décision** :

```
Task: "Create a security report from scan results"

Option 1 - Agent:
✅ Use Pentester agent
   - Needs judgment on threat severity
   - Requires security expertise
   - May need to chain multiple tools

Option 2 - Command:
❌ Too complex for automated workflow
   - Requires interpretation
   - Not fully procedural

Option 3 - Skill:
❌ Not just technical execution
   - Needs domain knowledge
   - Not just data transformation
```

---

## 7. Système d'Enforcement Multicouche {#enforcement-system}

### 7.1 Pourquoi un système d'enforcement ?

**Problème** : Claude ne lit pas toujours les fichiers de contexte même quand on lui dit de le faire.

**Solution** : Système à 4 couches qui rend presque impossible de l'ignorer.

### 7.2 Les 4 Couches d'Enforcement

#### Couche 1 : Context System Structure

La structure elle-même guide le chargement.

```
~/.claude/context/CLAUDE.md
    ↓ (explique toute l'architecture)
~/.claude/context/tools/CLAUDE.md
    ↓ (liste tous les outils)
~/.claude/context/projects/CLAUDE.md
    ↓ (overview des projets)
[project]/CLAUDE.md
    ↓ (pointe vers contextes spécifiques)
```

#### Couche 2 : Hook de Pre-Processing

**Fichier** : `~/.claude/hooks/user-prompt-submit-context-loader.ts`

Ce hook **intercepte chaque message** et ajoute des instructions avant que Claude ne le voie.

```typescript
/**
 * Hook: user-prompt-submit-context-loader
 * 
 * S'exécute sur CHAQUE prompt utilisateur.
 * Ajoute automatiquement des instructions de chargement de contexte.
 */

export default function onUserPromptSubmit(userMessage: string): string {
  // Instructions injectées AVANT chaque message
  const mandatoryPrefix = `
╔════════════════════════════════════════════════════════════╗
║  🚨 MANDATORY CONTEXT LOADING - EXECUTE IMMEDIATELY 🚨    ║
╔════════════════════════════════════════════════════════════╗

BEFORE responding to the user's message below, you MUST:

1. Use the Read tool on: ~/.claude/context/CLAUDE.md
   → This explains the entire context architecture

2. Use the Read tool on: ~/.claude/context/tools/CLAUDE.md
   → This documents all available tools and their usage

3. Use the Read tool on: ~/.claude/context/projects/CLAUDE.md
   → This provides overview of active projects

DO NOT claim you've read these files without actually using the Read tool.
The user will verify that you've loaded context by checking your actions.

Responses without proper context loading are INCORRECT and will be rejected.

════════════════════════════════════════════════════════════

USER'S ACTUAL MESSAGE:

${userMessage}
`;

  return mandatoryPrefix;
}
```

**Pourquoi ça marche** :
- Claude voit ces instructions **avant** le message utilisateur
- Les instructions sont **répétitives et insistantes**
- Le formatting visuel (emojis, boxes) attire l'attention
- Exige une **action observable** (Read tool)

#### Couche 3 : Instructions dans CLAUDE.md Principal

**Fichier** : `[project]/CLAUDE.md` (à la racine de chaque projet)

```markdown
# 🚨🚨🚨 MANDATORY FIRST ACTION - DO THIS IMMEDIATELY 🚨🚨🚨

## SESSION STARTUP REQUIREMENT (NON-NEGOTIABLE)

**BEFORE DOING OR SAYING ANYTHING, YOU MUST:**

1. **SILENTLY AND IMMEDIATELY READ THESE FILES (using Read tool):**
   - `~/.claude/context/CLAUDE.md` - The complete context system documentation
   - `~/.claude/context/tools/CLAUDE.md` - All available tools and their usage
   - `~/.claude/context/projects/CLAUDE.md` - Active projects overview

2. **SILENTLY SCAN:** `~/.claude/commands/` directory (using LS tool) to see available commands

3. **ONLY AFTER ACTUALLY READING ALL FILES, then acknowledge:**

   ✅ Context system loaded - I understand the context architecture.
   ✅ Tools context loaded - I know my commands and capabilities.
   ✅ Projects loaded - I'm aware of active projects and their contexts.

**DO NOT LIE ABOUT LOADING THESE FILES. ACTUALLY LOAD THEM FIRST.**

**FAILURE TO ACTUALLY LOAD BEFORE CLAIMING = LYING TO USER**

---

You cannot properly respond to ANY request without ACTUALLY READING:
- The complete context system architecture (from context/CLAUDE.md)
- Your tools and when to use them (from context/tools/CLAUDE.md)
- Active projects and their contexts (from context/projects/CLAUDE.md)
- Available commands (from commands/ directory)

**THIS IS NOT OPTIONAL. ACTUALLY DO THE READS BEFORE THE CHECKMARKS.**

---

[Rest of project-specific content...]
```

**Éléments clés** :
- ❗ **Langage agressif** : "NON-NEGOTIABLE", "DO NOT LIE"
- 🔴 **Emojis urgents** : Créent une barrière psychologique
- ✅ **Checkmarks explicites** : Obligation de confirmer après lecture
- 🛠️ **Actions observables** : Doit utiliser Read tool (prouvable)

#### Couche 4 : Symlinks de Redondance

**Structure** :

```
~/.claude/
├── CLAUDE.md                    # Symlink → context/CLAUDE.md
├── context/
│   └── CLAUDE.md                # Fichier réel
└── [project]/
    └── CLAUDE.md                # Pointe vers ~/.claude/context/...
```

**Pourquoi** : Si Claude cherche dans différents emplacements, il trouvera toujours les instructions.

### 7.3 Vérification de l'Enforcement

**Comment savoir si ça marche ?**

Quand Claude démarre une session, vous devriez voir :

```
// Claude's first actions
[Read tool] ~/.claude/context/CLAUDE.md (Reading...)
[Read tool] ~/.claude/context/tools/CLAUDE.md (Reading...)  
[Read tool] ~/.claude/context/projects/CLAUDE.md (Reading...)
[LS tool] ~/.claude/commands/ (Listing...)

✅ Context system loaded - I understand the context architecture.
✅ Tools context loaded - I know my commands and capabilities.
✅ Projects loaded - I'm aware of active projects and their contexts.

Now, how can I help you today?
```

**Si Claude saute directement à répondre** : Le système d'enforcement doit être renforcé.

### 7.4 Debugging du Système d'Enforcement

**Problème** : Claude ne charge pas le contexte.

**Solutions par couche** :

**Couche 1** : Vérifier structure de fichiers
```bash
ls -la ~/.claude/context/
# Doit contenir CLAUDE.md, tools/, projects/, etc.
```

**Couche 2** : Vérifier le hook
```bash
cat ~/.claude/hooks/user-prompt-submit-context-loader.ts
# Hook doit être présent et bien formaté
```

**Couche 3** : Renforcer CLAUDE.md
```markdown
# Ajouter au début de CLAUDE.md :

⛔⛔⛔ STOP - READ THIS FIRST ⛔⛔⛔

CRITICAL FAILURE WILL OCCUR IF YOU SKIP THIS STEP.

IMMEDIATELY use Read tool on:
1. ~/.claude/context/CLAUDE.md
2. ~/.claude/context/tools/CLAUDE.md
3. ~/.claude/context/projects/CLAUDE.md

DO NOT proceed without reading. DO NOT lie about reading.
```

**Couche 4** : Tester manuellement
```
// Demander explicitement à Claude
"Before we start, please read:
- ~/.claude/context/CLAUDE.md
- ~/.claude/context/tools/CLAUDE.md
- ~/.claude/context/projects/CLAUDE.md

And confirm you've loaded them."
```

---

## 8. Plan de migration depuis Aria {#migration-plan}

### 8.1 Audit de votre système Aria actuel

**Phase 1 : Inventaire (1-2 jours)**

Créez un document d'audit :

```markdown
# Audit Système Aria - [Date]

## 1. Structure actuelle

### Fichiers de configuration
- Où sont vos configurations Claude ?
- Combien de CLAUDE.md différents ?
- Taille moyenne des CLAUDE.md ?

### Organisation du contexte  
- Comment organisez-vous le contexte ?
- Y a-t-il duplication d'information ?
- Quels types de contexte avez-vous ?
  - [ ] Instructions générales
  - [ ] Contexte projet
  - [ ] Outils & commandes
  - [ ] Agents / personas
  - [ ] Standards & principes

### Outils & intégrations
- Quels MCP servers utilisez-vous ?
- Avez-vous des scripts custom ?
- Utilisez-vous des commandes récurrentes ?

### Agents & workflows
- Avez-vous des agents définis ?
- Quels workflows automatisez-vous ?
- Y a-t-il des processus répétitifs ?

## 2. Points de douleur

### Problèmes actuels
- [ ] CLAUDE.md trop volumineux
- [ ] Duplication de contexte
- [ ] Maintenance difficile
- [ ] Claude ignore les instructions
- [ ] Manque de structure claire
- [ ] Outils mal documentés
- [ ] Autre : ___________

### Objectifs de migration
1. [Votre objectif 1]
2. [Votre objectif 2]
3. [Votre objectif 3]

## 3. Ressources existantes à migrer

### Contextes à préserver
- [ ] Standards d'écriture
- [ ] Principes d'architecture
- [ ] Documentation technique
- [ ] Workflows spécifiques
- [ ] Autre : ___________

### Intégrations à conserver
- [ ] MCP servers : [liste]
- [ ] APIs externes : [liste]
- [ ] Scripts : [liste]
```

### 8.2 Phase de Préparation

**Semaine 1 : Setup de la structure de base**

```bash
# 1. Créer la structure KAI de base
mkdir -p ~/.claude/{context,agents,commands,hooks,skills}
mkdir -p ~/.claude/context/{memory,projects,tools,methodology,philosophy,architecture,testing,troubleshooting,working}
mkdir -p ~/.claude/context/working/{active,archive}
mkdir -p ~/.claude/skills/{public,user,example}

# 2. Créer le fichier maître de contexte
cat > ~/.claude/context/CLAUDE.md << 'EOF'
# KAI Context System - Master Documentation

[Copier le template de la section 3.2]
EOF

# 3. Créer le fichier tools hub
cat > ~/.claude/context/tools/CLAUDE.md << 'EOF'
# Tools Hub - Complete Documentation

[Copier le template de la section 4.3]
EOF

# 4. Créer le hook d'enforcement
cat > ~/.claude/hooks/user-prompt-submit-context-loader.ts << 'EOF'
[Copier le template de la section 7.2]
EOF

# 5. Copier votre .mcp.json existant
cp ~/.config/claude/mcp.json ~/.claude/.mcp.json

# 6. Créer le projects overview
cat > ~/.claude/context/projects/CLAUDE.md << 'EOF'
# Projects Overview

[Liste de vos projets avec liens vers leurs contextes]
EOF
```

### 8.3 Phase de Migration

**Semaine 2-3 : Migration du contexte**

**Étape 1 : Extraire et catégoriser**

Pour chaque CLAUDE.md existant dans Aria :

```bash
# Script d'aide à la catégorisation
#!/bin/bash
# categorize-context.sh

# Analyser un CLAUDE.md existant
echo "Analyzing: $1"
echo ""
echo "Identify sections in this file that belong to:"
echo "  1. memory/ - Learnings, preferences"
echo "  2. projects/ - Project-specific context"
echo "  3. tools/ - Tool documentation"
echo "  4. methodology/ - Structured approaches"
echo "  5. philosophy/ - Principles, beliefs"
echo "  6. architecture/ - Design patterns"
echo "  7. testing/ - Testing strategies"
echo ""
echo "Create separate files for each category."
```

**Étape 2 : Migrer par catégorie**

**Exemple : Migration d'instructions d'écriture**

Aria (avant) :
```markdown
# CLAUDE.md (racine projet website)

[... 500 lignes de contexte général ...]

## Writing Standards

- Use conversational tone
- Short paragraphs (2-3 sentences)
- Include examples
- Bold key concepts
- [... 100 lignes supplémentaires ...]

[... plus de contexte ...]
```

KAI (après) :

**Fichier 1** : `~/.claude/context/projects/website/content/CLAUDE.md`
```markdown
# Website Content - Writing Standards

## Tone & Style

- Conversational, approachable tone
- Short paragraphs (2-3 sentences max)
- Liberal use of examples
- Bold key concepts for scannability

[... reste des standards d'écriture ...]

## Related Contexts

- Overall philosophy: ~/.claude/context/philosophy/writing-philosophy.md
- Technical documentation standards: ~/.claude/context/documentation/standards.md
```

**Fichier 2** : `~/projects/website/CLAUDE.md` (minimal)
```markdown
# Website Project

## Content Creation

For content writing standards:
→ See: ~/.claude/context/projects/website/content/CLAUDE.md

## Development Guidelines

For technical setup:
→ See: ~/.claude/context/projects/website/CLAUDE.md

## Agents to Use

- Content: ~/.claude/agents/writer.md
- Development: ~/.claude/agents/engineer.md
```

**Étape 3 : Migrer les agents**

Si vous aviez des personas dans Aria :

```bash
# Pour chaque persona / agent existant
# Créer un fichier dédié dans ~/.claude/agents/

# Exemple :
cat > ~/.claude/agents/writer.md << 'EOF'
[Utiliser le template de la section 6.2]
EOF
```

**Étape 4 : Migrer les commandes**

Pour vos workflows automatisés :

```bash
# Pour chaque workflow répétitif
# Créer un fichier de command

# Exemple :
cat > ~/.claude/commands/publish-article.md << 'EOF'
# Publish Article Command

## Purpose
Publishes a blog article with all necessary steps.

## Process
1. Validate article format
2. Generate header image (if missing)
3. Commit to Git
4. Trigger deployment
5. Post to social media

[...]
EOF
```

### 8.4 Phase de Test

**Semaine 4 : Validation**

**Test 1 : Enforcement fonctionne**

```
1. Lancer Claude Code dans un projet
2. Observer si Claude charge automatiquement le contexte
3. Vérifier les checkmarks :
   ✅ Context system loaded
   ✅ Tools context loaded
   ✅ Projects loaded
```

**Test 2 : Contexte est accessible**

```
// Demander à Claude
"What tools do you have access to?"

// Claude devrait lister vos outils depuis
// ~/.claude/context/tools/CLAUDE.md
```

**Test 3 : Agents fonctionnent**

```
"Use the writer agent to create an article about [topic]"

// Claude devrait :
1. Charger l'agent writer.md
2. Charger le contexte d'écriture
3. Produire selon les standards
```

**Test 4 : Workflow complet**

```
"I need to create a new feature for [project]"

// Claude devrait :
1. Charger le contexte projet
2. Utiliser l'agent engineer
3. Suivre le workflow défini
4. Utiliser les bons outils
```

### 8.5 Phase de Raffinement

**Semaine 5+ : Itération**

**Monitorer** :
- Quelles parties du contexte Claude charge le plus souvent ?
- Quels contextes sont rarement utilisés ?
- Y a-t-il des gaps dans la documentation ?

**Optimiser** :
- Consolider les contextes rarement utilisés
- Séparer les contextes trop volumineux
- Améliorer les descriptions d'outils

**Documenter les learnings** :
```bash
# Ajouter à la mémoire système
echo "## [Date] - Learning" >> ~/.claude/context/memory/learnings.md
echo "- [Ce qui a bien fonctionné]" >> ~/.claude/context/memory/learnings.md
echo "- [Ce qui doit être amélioré]" >> ~/.claude/context/memory/learnings.md
```

### 8.6 Checklist de Migration Complète

```markdown
# Migration Aria → KAI : Checklist

## Phase 0 : Préparation
- [ ] Audit système Aria actuel
- [ ] Identification des points de douleur
- [ ] Documentation des objectifs

## Phase 1 : Setup Infrastructure
- [ ] Structure de répertoires créée
- [ ] CLAUDE.md maître configuré
- [ ] Tools hub créé
- [ ] Hook d'enforcement installé
- [ ] .mcp.json migré

## Phase 2 : Migration Contexte
- [ ] Contextes projets migrés
- [ ] Instructions d'écriture migrées
- [ ] Standards techniques migrés
- [ ] Philosophie & principes documentés
- [ ] Architecture & patterns documentés

## Phase 3 : Migration Agents
- [ ] Liste des agents définis
- [ ] Fichiers agents créés
- [ ] Contextes agents liés

## Phase 4 : Migration Commands
- [ ] Workflows identifiés
- [ ] Commands créées
- [ ] Commands documentées dans tools/

## Phase 5 : Migration Skills
- [ ] Skills publics activés
- [ ] Skills custom créés
- [ ] Skills documentés dans tools/

## Phase 6 : Tests
- [ ] Enforcement vérifié
- [ ] Contexte accessible
- [ ] Agents fonctionnels
- [ ] Commands opérationnelles
- [ ] Skills activés

## Phase 7 : Documentation
- [ ] README projet mis à jour
- [ ] Learnings documentés
- [ ] Best practices identifiées

## Phase 8 : Optimisation
- [ ] Contextes optimisés
- [ ] Descriptions améliorées
- [ ] Workflows raffinés
```

---

## 9. Exemples concrets et templates {#exemples-templates}

### 9.1 Exemple complet : Projet Blog

**Structure** :

```
~/projects/my-blog/
├── CLAUDE.md                          # Pointeur minimal
├── .claude/
│   └── skills/
│       └── seo-optimizer/             # Skill custom projet
│           └── SKILL.md
└── content/
    └── articles/

~/.claude/
├── context/
│   ├── projects/
│   │   └── my-blog/
│   │       ├── CLAUDE.md              # Config principale
│   │       ├── content/
│   │       │   └── CLAUDE.md          # Standards écriture
│   │       └── seo/
│   │           └── guidelines.md
│   └── tools/
│       └── CLAUDE.md                  # Hub outils (liste commands/skills)
├── agents/
│   └── writer.md                      # Agent d'écriture
└── commands/
    ├── write-blog-post.md
    ├── create-custom-image.md
    └── publish-article.md
```

**Contenu des fichiers** :

**`~/projects/my-blog/CLAUDE.md`** :
```markdown
# My Blog Project

## 🚨 MANDATORY COMPLIANCE PROTOCOL 🚨

## Context Loading

### Blog Configuration
→ See: ~/.claude/context/projects/my-blog/CLAUDE.md

### Content Standards
→ See: ~/.claude/context/projects/my-blog/content/CLAUDE.md

### SEO Guidelines
→ See: ~/.claude/context/projects/my-blog/seo/guidelines.md

## Required Actions

### Use Writer Agent for ALL Content
→ Agent: ~/.claude/agents/writer.md

### Available Commands
- `/command write-blog-post` - Create new article
- `/command create-custom-image` - Generate header image
- `/command publish-article` - Publish to website

### Project-Specific Skill
→ Skill: ./.claude/skills/seo-optimizer/ (auto-loads for SEO tasks)
```

**`~/.claude/context/projects/my-blog/CLAUDE.md`** :
```markdown
# My Blog - Project Configuration

## Overview

Personal blog focused on [your niche]. Built with [technology].

## Target Audience

- [Demographic 1]
- [Demographic 2]
- Reading level: [level]

## Content Strategy

### Article Types
1. **Tutorials** (60%)
   - Practical, step-by-step
   - 2000-3000 words
   - Code examples required

2. **Opinion Pieces** (30%)
   - Thought leadership
   - 1000-1500 words
   - Personal perspective

3. **Announcements** (10%)
   - Product launches
   - 500-800 words

## Technical Setup

### Stack
- Static site generator: [tool]
- Hosting: [platform]
- CMS: [if applicable]

### Deployment
- Command: `npm run deploy`
- Triggered by: Git push to main

## Related Contexts

- Content standards: ./content/CLAUDE.md
- SEO guidelines: ./seo/guidelines.md
- Writing philosophy: ~/.claude/context/philosophy/writing-philosophy.md
```

**`~/.claude/context/projects/my-blog/content/CLAUDE.md`** :
```markdown
# My Blog - Content Standards

## Writing Style

### Tone
- Conversational but professional
- Use "you" and "we" freely
- Inject personality

### Structure
- **Introduction** (1-2 paragraphs)
  - Hook
  - Context
  - Promise (what reader will learn)

- **Body** (organized sections)
  - H2 for main sections
  - H3 for subsections
  - 2-3 paragraphs per section max

- **Conclusion** (1 paragraph)
  - Summarize key points
  - Call to action

### Formatting
- **Bold** for key concepts (2-3 per section)
- `Code` for technical terms
- > Blockquotes for important insights
- Lists for steps or options

### Examples Required
- At least one concrete example per main section
- Code examples for tutorials
- Real-world scenarios

## SEO Requirements

- Primary keyword in: title, first paragraph, conclusion
- 2-3 H2 headers with keyword variations
- Meta description: 150-160 characters
- Alt text on all images

## Image Guidelines

- Header image: 1200x630px
- Format: WebP (or PNG fallback)
- Generated using create-custom-image command
- Alt text required

## Voice & Perspective

### Do:
✅ Share personal experiences
✅ Admit when you don't know something
✅ Use humor appropriately
✅ Challenge conventional wisdom

### Avoid:
❌ Buzzwords without explanation
❌ Jargon without context
❌ Absolute statements without nuance
❌ Clickbait titles

## Quality Checklist

Before publishing, verify:
- [ ] Title is compelling (50-60 characters)
- [ ] Introduction hooks reader
- [ ] Each section delivers value
- [ ] Examples are clear and relevant
- [ ] Code (if any) is tested
- [ ] Conclusion has clear takeaway
- [ ] SEO optimized
- [ ] Images have alt text
- [ ] Links are valid
- [ ] Proofread for typos
```

**Workflow typique** :

```
User: "Write an article about [topic]"
    ↓
Claude:
  1. Reads ~/projects/my-blog/CLAUDE.md (pointeur)
  2. Loads ~/.claude/context/projects/my-blog/content/CLAUDE.md
  3. Activates ~/.claude/agents/writer.md
  4. Uses ~/.claude/commands/write-blog-post.md
  5. Generates content following standards
  6. Uses ~/.claude/commands/create-custom-image.md for header
  7. Applies ./.claude/skills/seo-optimizer/ (if activated)
  8. Outputs formatted article
```

### 9.2 Exemple : Configuration MCP Servers

**`~/.claude/.mcp.json`** :

```json
{
  "mcpServers": {
    "playwright": {
      "command": "bunx",
      "args": ["@playwright/mcp@latest"],
      "env": {
        "NODE_ENV": "production"
      }
    },
    "google-drive": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-google-drive"
      ],
      "env": {
        "GOOGLE_CLIENT_ID": "${GOOGLE_CLIENT_ID}",
        "GOOGLE_CLIENT_SECRET": "${GOOGLE_CLIENT_SECRET}"
      }
    },
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "custom-api": {
      "type": "http",
      "url": "https://api.example.com/mcp",
      "headers": {
        "Authorization": "Bearer ${API_TOKEN}",
        "X-API-Key": "${API_KEY}"
      },
      "description": "Custom company API for internal data"
    }
  }
}
```

**Documentation dans `~/.claude/context/tools/CLAUDE.md`** :

```markdown
# Tools Hub - MCP Servers

## Available MCP Servers

### playwright
**Type**: Local executable
**Purpose**: Browser automation, web scraping, testing
**Usage**: Automatically available for web interactions

**Common tasks**:
- "Scrape data from [URL]"
- "Test this webpage's functionality"
- "Take screenshot of [URL]"

### google-drive
**Type**: OAuth integration
**Purpose**: Access files, docs, spreadsheets from Google Drive
**Usage**: Automatically discovered when mentioning Drive files

**Common tasks**:
- "Find my document about [topic]"
- "Read the spreadsheet named [name]"
- "Search Drive for files matching [criteria]"

**Authentication**: First use requires OAuth flow

### github
**Type**: Personal Access Token
**Purpose**: Repository management, issues, PRs
**Usage**: Automatically available for GitHub operations

**Common tasks**:
- "Create issue for [bug]"
- "List PRs in [repo]"
- "Show recent commits"

**Setup**: Requires GITHUB_TOKEN environment variable

### custom-api
**Type**: HTTP API
**Purpose**: Access to internal company data
**Usage**: Query company-specific information

**Endpoints**:
- `/projects` - List all projects
- `/team` - Team member info
- `/metrics` - Analytics data

**Authentication**: Token-based (configured)

## MCP Troubleshooting

### Server not responding
1. Check if server is configured in .mcp.json
2. Verify authentication credentials
3. Test server independently
4. Check logs: `~/.claude/logs/mcp-[server-name].log`

### Authentication issues
1. Verify environment variables are set
2. For OAuth: re-authenticate if needed
3. For token auth: check token validity

### Performance issues
1. Some servers are slow for large datasets
2. Consider local caching
3. Limit query scope
```

### 9.3 Template : Skill Custom

**Cas d'usage** : Créer un skill pour analyser les logs d'erreur

**`~/.claude/skills/user/error-log-analyzer/SKILL.md`** :

```markdown
---
name: error-log-analyzer
description: Analyzes error logs, identifies patterns, suggests fixes
version: "1.0.0"
author: "Your Name"
tags: ["debugging", "logs", "error-analysis"]
---

# Error Log Analyzer Skill

Specialized skill for analyzing error logs, identifying common patterns,
and suggesting fixes based on error types and frequency.

## When to Use This Skill

Use this skill when:
- User mentions "error log", "stack trace", or "crash report"
- User provides a log file or error output
- User asks to "debug" or "analyze errors"
- File extensions: .log, .err, .trace

## Capabilities

1. **Parse logs** - Extract structured error information
2. **Identify patterns** - Find recurring errors
3. **Classify severity** - Critical, warning, info
4. **Suggest fixes** - Common solutions for known errors
5. **Generate report** - Summarized analysis with recommendations

## Process

### Step 1: Ingest Log Data

Accept log data in multiple formats:
- Direct paste of log content
- File path to log file
- URL to remote log

```bash
# Read log file
cat /path/to/error.log

# Or if remote
curl https://example.com/logs/error.log
```

### Step 2: Parse and Structure

Extract key information:
- Timestamp
- Error level (ERROR, WARN, INFO)
- Error message
- Stack trace (if applicable)
- Context (file, line number, function)

### Step 3: Analyze Patterns

Identify:
- Most frequent errors (top 10)
- Error trends over time
- Correlated errors
- Critical vs. non-critical

### Step 4: Classify Errors

Categories:
- **Syntax errors** - Code issues
- **Runtime errors** - Execution problems
- **Network errors** - Connectivity issues
- **Database errors** - Data access problems
- **Permission errors** - Access denied
- **Resource errors** - Memory, disk, CPU
- **Unknown** - Unclassified

### Step 5: Suggest Fixes

For known error patterns:
- Provide specific fix steps
- Reference documentation
- Suggest debugging approach

For unknown errors:
- Provide general debugging strategy
- Suggest information to gather
- Recommend resources

### Step 6: Generate Report

Create structured report:
1. **Executive Summary**
   - Total errors: X
   - Critical: Y
   - Top issue: Z

2. **Error Breakdown**
   - By category
   - By frequency
   - By severity

3. **Recommendations**
   - Immediate fixes (critical)
   - Short-term improvements
   - Long-term solutions

4. **Action Items**
   - Prioritized list
   - Effort estimates

## Error Pattern Database

### Common Patterns & Fixes

#### Pattern: "Cannot read property 'X' of undefined"
**Cause**: Accessing property on undefined object
**Fix**:
```javascript
// Before
const value = obj.property;

// After
const value = obj?.property || defaultValue;
```

#### Pattern: "ECONNREFUSED"
**Cause**: Cannot connect to server/service
**Fix**:
1. Check if service is running
2. Verify host/port are correct
3. Check firewall rules
4. Verify network connectivity

[... more patterns ...]

## Output Format

Generate report as Markdown:

```markdown
# Error Log Analysis Report
**Date**: [timestamp]
**Log Source**: [source]
**Analysis Period**: [time range]

## Summary
- Total Errors: [count]
- Critical: [count] ⚠️
- Warnings: [count]
- Info: [count]

## Top Issues

### 1. [Error Category] - [Frequency]%
**Message**: [error message]
**Occurrences**: [count]
**First Seen**: [timestamp]
**Last Seen**: [timestamp]

**Impact**: [Critical/High/Medium/Low]

**Suggested Fix**:
[Step-by-step fix]

**References**:
- [Documentation link]
- [Stack Overflow link]

[... repeat for top 5-10 issues ...]

## Recommendations

### Immediate Actions (Do Today)
1. [Action item 1]
2. [Action item 2]

### Short-term (This Week)
1. [Improvement 1]
2. [Improvement 2]

### Long-term (This Month)
1. [Strategic fix 1]
2. [Strategic fix 2]

## Appendix

### Full Error List
[Detailed list or link to spreadsheet]

### Analysis Methodology
[How analysis was performed]
```

## Advanced Usage

### Multi-Log Analysis

Compare logs from multiple sources:
```bash
# Analyze multiple logs
analyze-errors \
  --logs app1.log,app2.log,database.log \
  --compare \
  --find-correlations
```

### Time-based Analysis

Focus on specific time periods:
```bash
# Errors in last 24 hours
analyze-errors \
  --log error.log \
  --since "24 hours ago"
```

### Integration with Alerting

Set thresholds for alerts:
- Critical error count > X → immediate alert
- Error rate increase > Y% → warning
- New error types → notification

## Examples

### Example 1: Web Application Error Log

**Input**: Node.js application error log

**Output**: Report identifying:
- Top issue: Database connection timeout (40% of errors)
- Suggested fix: Increase connection pool size
- Secondary issue: Memory leaks in specific route
- Suggested fix: Review image processing logic

### Example 2: System Log Analysis

**Input**: Linux syslog file

**Output**: Report showing:
- Critical: Disk space warnings (5 instances)
- Immediate action: Clean up /var/log
- Warning: High CPU usage on specific processes
- Investigation needed: Identify resource-heavy operations

## Testing This Skill

To verify functionality:

1. **Test with sample log**:
   ```
   Use the error-log-analyzer skill to analyze this log:
   [paste sample log with known errors]
   ```

2. **Expected output**:
   - Structured report
   - Top 3-5 errors identified
   - Specific fix suggestions
   - Prioritized action items

3. **Verification**:
   - Check if known errors are caught
   - Verify fix suggestions are relevant
   - Confirm report format is correct

## Continuous Improvement

Track skill effectiveness:
- Which error patterns are most common?
- Are suggested fixes effective?
- What new patterns should be added?

Update pattern database regularly based on:
- User feedback
- New error types encountered
- Updated best practices

## Related Resources

- Context: ~/.claude/context/troubleshooting/CLAUDE.md
- Agent: ~/.claude/agents/engineer.md (for implementing fixes)
- Command: May integrate with `debug-issue` command

## Maintenance

**Version History**:
- 1.0.0 (2025-01-XX): Initial release
- [Future versions here]

**Known Limitations**:
- Requires structured log format
- May miss obfuscated errors
- Limited to predefined patterns (extensible)

**Future Enhancements**:
- Machine learning for pattern detection
- Integration with monitoring tools
- Automated fix application
```

---

## 10. Best Practices et optimisations {#best-practices}

### 10.1 Principles d'Organisation

**Principe #1 : Single Source of Truth**

❌ **Mauvais** :
```
~/project1/CLAUDE.md
  → Contains writing standards

~/project2/CLAUDE.md
  → Contains SAME writing standards (duplicated)
```

✅ **Bon** :
```
~/.claude/context/philosophy/writing-standards.md
  ← Single source

~/project1/CLAUDE.md
  → See: ~/.claude/context/philosophy/writing-standards.md

~/project2/CLAUDE.md
  → See: ~/.claude/context/philosophy/writing-standards.md
```

**Principe #2 : Granularité Appropriée**

❌ **Trop granulaire** :
```
~/.claude/context/
├── button-color-preferences.md       # Trop spécifique
├── link-hover-state-preferences.md   # Trop spécifique
└── font-size-preferences.md          # Trop spécifique
```

✅ **Granularité appropriée** :
```
~/.claude/context/
└── philosophy/
    └── design-preferences/
        └── ui-standards.md            # Groupe les préférences
```

❌ **Pas assez granulaire** :
```
~/.claude/context/
└── everything.md                      # 5000 lignes de tout
```

✅ **Bon équilibre** :
```
~/.claude/context/
├── projects/
│   ├── website/
│   │   ├── CLAUDE.md                 # Overview
│   │   ├── content/
│   │   │   └── CLAUDE.md             # Writing specific
│   │   └── development/
│   │       └── CLAUDE.md             # Dev specific
```

**Principe #3 : Progressive Disclosure**

Chargez le contexte par niveaux de détail :

```
Niveau 1 : CLAUDE.md minimal (pointeurs)
    ↓
Niveau 2 : Context overviews (grandes lignes)
    ↓
Niveau 3 : Detailed contexts (spécifiques)
    ↓
Niveau 4 : Referenced resources (quand nécessaire)
```

### 10.2 Optimisation du Context Window

**Stratégie #1 : Lazy Loading**

Ne chargez que le nécessaire :

```markdown
# Projet CLAUDE.md

## Context pour tasks de dev
Pour développement :
→ See: ~/.claude/context/projects/myapp/development/CLAUDE.md

## Context pour content
Pour contenu :
→ See: ~/.claude/context/projects/myapp/content/CLAUDE.md

# Ne pas charger les deux simultanément
```

**Stratégie #2 : Conditional Loading**

Utilisez des conditions :

```markdown
# Agent Engineer

## Context Loading

If working on backend:
→ Read: ~/.claude/context/architecture/backend-patterns.md

If working on frontend:
→ Read: ~/.claude/context/architecture/frontend-patterns.md

If working on database:
→ Read: ~/.claude/context/architecture/database-design.md
```

**Stratégie #3 : Référencement plutôt que Duplication**

```markdown
# ❌ Mauvais - Duplication
## Testing Standards
- Use Jest for unit tests
- Use Playwright for E2E
- Maintain 80% coverage
[... 50 lignes de détails ...]

# ✅ Bon - Référencement
## Testing Standards
→ See: ~/.claude/context/testing/testing-guidelines.md
```

### 10.3 Maintenance du Système

**Routine Quotidienne** :

```bash
# Script: daily-maintenance.sh

#!/bin/bash

# 1. Backup context
cp -r ~/.claude/context ~/.claude/backups/context-$(date +%Y%m%d)

# 2. Check for broken references
echo "Checking for broken context references..."
grep -r "See: " ~/.claude/context/ | while read ref; do
  file=$(echo "$ref" | sed 's/.*See: \(.*\)/\1/')
  if [ ! -f "$file" ]; then
    echo "❌ Broken reference: $file"
  fi
done

# 3. Find large files
echo "Large context files (>1000 lines):"
find ~/.claude/context -name "*.md" -exec wc -l {} \; | \
  awk '$1 > 1000 {print $0}' | \
  sort -rn

# 4. Update learnings
echo "Don't forget to update ~/.claude/context/memory/learnings.md"
```

**Routine Hebdomadaire** :

```markdown
# Weekly Review Checklist

## Context Audit
- [ ] Review most-loaded contexts (are they still optimal?)
- [ ] Check for outdated information
- [ ] Identify context that should be split/merged
- [ ] Update version numbers if relevant

## Tools Audit
- [ ] Verify all MCP servers are working
- [ ] Update tool descriptions if behavior changed
- [ ] Add new tools discovered this week
- [ ] Remove deprecated tools

## Agents Audit
- [ ] Review agent performance
- [ ] Update agent instructions based on learnings
- [ ] Check if agents need new context references
- [ ] Verify agent collaboration is smooth

## Learning Documentation
- [ ] Document what worked well this week
- [ ] Document what didn't work
- [ ] Update patterns discovered
- [ ] Add to troubleshooting guides
```

**Routine Mensuelle** :

```markdown
# Monthly Deep Review

## Strategic Assessment
- [ ] Are projects in context still active?
- [ ] Archive completed projects
- [ ] Update project priorities
- [ ] Reassess context organization

## Skills Review
- [ ] Which skills were most used?
- [ ] Which skills need improvement?
- [ ] Are there gaps that new skills could fill?
- [ ] Update skill descriptions

## Performance Analysis
- [ ] How effective is the enforcement system?
- [ ] Are context loading times acceptable?
- [ ] Is Claude finding what it needs quickly?
- [ ] Any patterns in Claude's mistakes?

## System Evolution
- [ ] What new capabilities are needed?
- [ ] What can be deprecated?
- [ ] Are there new Anthropic features to integrate?
- [ ] Should any structure be reorganized?
```

### 10.4 Patterns Anti-patterns

**✅ Bons Patterns**

**Pattern : Contexte en Cascade**
```
General Philosophy
    ↓
Project Philosophy
    ↓
Specific Task Context
```

**Pattern : Agent Specialization**
```
Engineer Agent → Backend Sub-agent
               ↘ Frontend Sub-agent
               ↘ DevOps Sub-agent
```

**Pattern : Tool Orchestration**
```
High-level Command
    ↓
Calls multiple lower-level tools
    ↓
Produces integrated result
```

**❌ Anti-patterns**

**Anti-pattern : Circular References**
```markdown
# file-a.md
→ See: file-b.md

# file-b.md
→ See: file-a.md
```

**Anti-pattern : Over-specification**
```markdown
# ❌ Trop détaillé pour contexte général
When writing a function:
1. First, type the word "function"
2. Then add a space
3. Then type the function name
4. Then add parentheses
[... 500 lignes de détails excessifs ...]
```

**Anti-pattern : Context Stale**
```markdown
# ❌ Contexte obsolète jamais mis à jour
## We use React 16
[... mais le projet utilise maintenant React 18 ...]
```

**Anti-pattern : Mega-files**
```markdown
# ❌ Un fichier géant de 5000 lignes
# Tout mélangé : projects, tools, agents, everything
```

### 10.5 Debugage de Problèmes Courants

**Problème : Claude n'utilise pas les bons outils**

**Diagnostic** :
```
1. Vérifier ~/.claude/context/tools/CLAUDE.md
   - Les outils sont-ils documentés ?
   - Les descriptions sont-elles claires ?

2. Vérifier si MCP servers fonctionnent :
   # Test MCP server
   npx @anthropic-ai/mcp-client test [server-name]

3. Vérifier logs :
   tail -f ~/.claude/logs/mcp-*.log
```

**Solution** :
```markdown
# Améliorer les descriptions d'outils

❌ Avant :
"playwright: browser stuff"

✅ Après :
"playwright: Browser automation for web scraping, testing,
and screenshots. Use when user mentions websites, URLs,
or browser interactions."
```

**Problème : Claude ignore le contexte**

**Diagnostic** :
```
1. Hook fonctionne-t-il ?
   cat ~/.claude/hooks/user-prompt-submit-context-loader.ts

2. CLAUDE.md a-t-il les instructions d'enforcement ?
   head -50 [project]/CLAUDE.md

3. Claude charge-t-il effectivement les fichiers ?
   Observer les tool calls dans l'interface
```

**Solution** :
```markdown
# Renforcer l'enforcement

1. Ajouter des emojis visuels : 🚨⛔❌✅
2. Utiliser CAPS pour insister : "MANDATORY", "CRITICAL"
3. Répéter les instructions à plusieurs endroits
4. Exiger des actions observables (Read tool)
5. Inclure des conséquences : "Will fail without this"
```

**Problème : Contexte trop volumineux**

**Diagnostic** :
```
Symptômes :
- Context window saturé
- Réponses lentes
- Claude perd du contexte en milieu de conversation
```

**Solution** :
```
1. Séparer en fichiers plus petits
2. Utiliser progressive disclosure
3. Lazy loading conditionnel
4. Archiver contexte peu utilisé
```

**Problème : Maintenance difficile**

**Diagnostic** :
```
Symptômes :
- Duplication de contexte
- Informations contradictoires
- Difficile de trouver où changer quelque chose
```

**Solution** :
```
1. Établir Single Source of Truth
2. Créer index/hub files (comme tools/CLAUDE.md)
3. Utiliser références plutôt que duplication
4. Routine de maintenance régulière
```

### 10.6 Évolution du Système

**Comment faire évoluer KAI au fil du temps**

**Phase 1 : Setup Initial (Semaines 1-4)**
- Structure de base
- Contextes essentiels
- Quelques agents
- Enforcement basique

**Phase 2 : Consolidation (Mois 2-3)**
- Ajout de workflows spécifiques
- Création de skills custom
- Raffinement des agents
- Optimisation du contexte

**Phase 3 : Expansion (Mois 4-6)**
- Intégration MCP avancée
- Agents spécialisés multiples
- Commands complexes
- Orchestration multi-agents

**Phase 4 : Sophistication (Mois 6+)**
- Skills avancés avec code execution
- APIs personnelles (daemon)
- Automation poussée
- Système auto-améliorant

**Checklist d'Évolution** :

```markdown
# KAI System Evolution Checklist

## Capabilities to Add

### Short-term (Next Month)
- [ ] Skill: [specific capability needed]
- [ ] Agent: [specialized persona for new domain]
- [ ] Command: [workflow that's becoming repetitive]
- [ ] MCP Server: [integration needed]

### Medium-term (Next Quarter)
- [ ] Advanced orchestration: [multi-agent workflows]
- [ ] Custom APIs: [personal daemon services]
- [ ] Specialized skills: [domain-specific expertise]
- [ ] Automation hooks: [event-driven actions]

### Long-term (Next Year)
- [ ] Self-improving capabilities
- [ ] Cross-project intelligence
- [ ] Predictive context loading
- [ ] Full Digital Assistant capabilities

## Technical Debt to Address
- [ ] Refactor oversized context files
- [ ] Consolidate duplicated instructions
- [ ] Improve enforcement reliability
- [ ] Optimize context loading performance

## Documentation to Improve
- [ ] Better tool descriptions
- [ ] More agent examples
- [ ] Clearer workflow documentation
- [ ] Expanded troubleshooting guides

## System Health
- [ ] Audit unused contexts (archive if not used in 3 months)
- [ ] Update outdated information
- [ ] Verify all references are valid
- [ ] Test all critical workflows
```

---

## Conclusion

L'architecture KAI transforme Claude Code en un véritable **assistant numérique personnel** grâce à :

1. **Context Management Distribué** : Information organisée hiérarchiquement, chargée progressivement
2. **Enforcement Multi-couche** : Système robuste pour garantir le chargement du contexte
3. **Modularité** : Agents, Commands, Skills, MCP - chaque problème résolu une fois
4. **Progressive Disclosure** : Contexte chargé par niveaux selon besoin
5. **Single Source of Truth** : Pas de duplication, une source par information

### Prochaines étapes suggérées

1. **Commencez petit** : Structure de base + quelques contextes essentiels
2. **Itérez rapidement** : Testez, apprenez, ajustez
3. **Documentez** : Capturez vos learnings dans memory/
4. **Évoluez** : Ajoutez agents, skills, commands au fil du besoin
5. **Partagez** : Contribuez vos skills et patterns à la communauté

### Ressources additionnelles

- **Article KAI original** : https://danielmiessler.com/blog/personal-ai-infrastructure
- **Claude Code Docs** : https://docs.claude.com/en/docs/claude-code/overview
- **Anthropic Skills** : https://github.com/anthropics/skills
- **MCP Documentation** : https://modelcontextprotocol.io/

---

**Auteur** : Guide créé pour votre migration depuis Aria vers KAI  
**Date** : Novembre 2025  
**Version** : 1.0

*Ce guide évoluera avec vos besoins. Documentez vos modifications et learnings dans `~/.claude/context/memory/`.*
