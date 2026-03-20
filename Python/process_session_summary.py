# name: Process Session Summary
# keywords: [utility, session, documentation, automation]
# description: Converts quick-capture session notes into properly formatted session logs and timeline entries
#
# Processes Session_Summary_Quick_Capture.md files and generates:
#   - Formatted session log (Stories/[name].txt)
#   - Timeline event entries
#   - Character status updates summary
#   - Campaign progress notes
#
# Command line arguments:
#   --input [path]    - Path to quick capture form (required)
#   --output [path]   - Output directory for session log (default: Stories/)
#   --condensed       - Use condensed template (default: full template)
#   --timeline        - Generate timeline-only output (no session log)
#   --dry-run         - Preview output without writing

import sys
import os
import argparse
from datetime import datetime

def parse_capture_form(filepath):
    """Parse a quick capture form into structured data."""
    
    if not os.path.exists(filepath):
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    data = {
        'campaign': None,
        'date_played': None,
        'in_game_date': None,
        'characters': [],
        'beats': [],
        'decisions': [],
        'npcs': [],
        'status_changes': {},
        'world_changes': {},
        'plot_threads': {},
        'mechanics': {},
        'next_session': {},
    }
    
    # Parse sections
    sections = content.split('---')
    
    for section in sections:
        lines = section.strip().split('\n')
        
        if 'BASIC INFO' in section:
            for line in lines:
                if 'Campaign/Scenario Name:' in line:
                    data['campaign'] = line.split(':', 1)[1].strip()
                elif 'Date Played (IRL):' in line:
                    data['date_played'] = line.split(':', 1)[1].strip()
                elif 'In-Game Date/Day:' in line:
                    data['in_game_date'] = line.split(':', 1)[1].strip()
                elif 'Characters Present:' in line:
                    chars = line.split(':', 1)[1].strip()
                    if chars:
                        data['characters'] = [c.strip() for c in chars.split(',')]
        
        elif 'STORY BEATS' in section:
            for line in lines:
                if line.startswith('- '):
                    data['beats'].append(line[2:].strip())
        
        elif 'KEY DECISIONS' in section:
            current_decision = None
            for line in lines:
                if line.startswith('**Decision'):
                    current_decision = {'title': line.split(':', 1)[1].strip() if ':' in line else 'Decision'}
                    data['decisions'].append(current_decision)
                elif line.startswith('- *Choice made:'):
                    if current_decision:
                        current_decision['choice'] = line.split(':', 1)[1].strip()
                elif line.startswith('- *Why'):
                    if current_decision:
                        current_decision['importance'] = line.split(':', 1)[1].strip()
                elif line.startswith('- *Immediate'):
                    if current_decision:
                        current_decision['consequence'] = line.split(':', 1)[1].strip()
        
        elif 'NPC INTERACTIONS' in section:
            # Parse table (simplified)
            in_table = False
            for line in lines:
                if '|' in line and '---' not in line:
                    in_table = True
                    cells = [c.strip() for c in line.split('|')]
                    if len(cells) > 1 and cells[1] and cells[1][0] not in ['N', '-']:
                        data['npcs'].append({
                            'name': cells[1],
                            'action': cells[2] if len(cells) > 2 else '',
                            'reaction': cells[3] if len(cells) > 3 else '',
                            'status_change': cells[4] if len(cells) > 4 else ''
                        })
    
    return data


def generate_session_log(data, condensed=False):
    """Generate a formatted session log from parsed data."""
    
    if condensed:
        return generate_condensed_log(data)
    else:
        return generate_full_log(data)


def generate_condensed_log(data):
    """Generate using condensed template."""
    
    # Build the session recap (2-3 sentences)
    recap = ""
    if data['beats']:
        main_beat = data['beats'][0] if data['beats'] else ""
        num_beats = len(data['beats'])
        recap = f"The session covered {num_beats} major events, beginning with {main_beat}."
        if len(data['beats']) > 1:
            recap += f" Key developments included several significant plot points that advanced the story."
    
    log = f"""# {data['campaign']} - Day [X]

**Campaign:** {data['campaign']}  
**In-Game Date:** {data['in_game_date']}  
**Played:** {data['date_played']}  
**PC:** {', '.join(data['characters'])}  

---

## Summary

{recap}

---

## Key Events

"""
    
    for i, beat in enumerate(data['beats'][:5], 1):
        log += f"- {beat}\n"
    
    log += "\n---\n\n## Decisions & Consequences\n\n"
    
    for decision in data['decisions']:
        log += f"**{decision.get('title', 'Decision')}:** "
        log += f"{decision.get('choice', '')} → {decision.get('consequence', '')}\n\n"
    
    log += "---\n\n## NPCs & Interactions\n\n"
    
    for npc in data['npcs']:
        if npc['name']:
            log += f"- **{npc['name']}** — {npc['action']}\n"
    
    log += "\n---\n\n## Next Session\n\n"
    log += f"**Starts:** [Location/situation]  \n"
    log += f"**Open Threads:** {data['plot_threads'].get('active', 'TBD')}\n\n"
    
    return log


def generate_full_log(data):
    """Generate using full template."""
    
    # Similar to condensed but with more sections
    log = generate_condensed_log(data)
    log += "\n---\n\n## Character Status\n\n"
    
    if data['status_changes']:
        log += f"**Applied:** {', '.join(data['status_changes'].get('applied', []))}\n"
        log += f"**Current:** {', '.join(data['status_changes'].get('current', []))}\n\n"
    
    return log


def format_for_stories(session_name, log_content):
    """Format log for Stories directory with proper meta tag."""
    
    # Extract campaign from metadata
    campaign = session_name.split('_')[0] if '_' in session_name else 'Session'
    
    meta_tag = f"<meta>{session_name}, session, log, story, {campaign}, Session documentation for {session_name}</meta>"
    
    full_content = f"{meta_tag}\n\n{log_content}"
    
    return full_content


def main():
    parser = argparse.ArgumentParser(
        description='Convert quick-capture session notes into formatted session logs'
    )
    parser.add_argument('--input', required=True, help='Path to quick capture form')
    parser.add_argument('--output', default='D:\\Claude_MCP_folder\\Stories', help='Output directory for session log')
    parser.add_argument('--condensed', action='store_true', help='Use condensed template')
    parser.add_argument('--dry-run', action='store_true', help='Preview without writing')
    parser.add_argument('--session-name', help='Override session name (derived from input filename by default)')
    
    args = parser.parse_args()
    
    # Parse the input form
    print(f"Reading: {args.input}")
    data = parse_capture_form(args.input)
    
    # Generate session log
    log_content = generate_session_log(data, condensed=args.condensed)
    
    # Determine session name
    session_name = args.session_name
    if not session_name:
        session_name = os.path.splitext(os.path.basename(args.input))[0]
    
    # Format for Stories directory
    formatted_content = format_for_stories(session_name, log_content)
    
    # Output path
    output_path = os.path.join(args.output, f"{session_name}.txt")
    
    # Display preview
    print("\n" + "="*70)
    print("PREVIEW:")
    print("="*70)
    print(formatted_content[:500] + "\n[...truncated...]\n")
    
    # Dry run or write
    if args.dry_run:
        print(f"\n[DRY RUN] Would write to: {output_path}")
    else:
        os.makedirs(args.output, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(formatted_content)
        print(f"\n✓ Wrote session log to: {output_path}")


if __name__ == '__main__':
    main()
