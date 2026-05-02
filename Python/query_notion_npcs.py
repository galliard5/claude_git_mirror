# name: Query Notion NPCs
# keywords: [notion, database, npc, export, api]
# description: Query the Aethelmark NPCs database from Notion API and export all entries to a file
#
# Queries the Notion API to fetch all NPCs from the Aethelmark NPCs database.
# Handles pagination automatically and exports results to a JSON and plaintext file.
#
# Command line arguments:
#   --api-key KEY: Notion API key (required)
#   --dry-run: Preview without saving files
#   --output FILE: Output filename (default: aethelmark_npcs_export.json)

import json
import urllib.request
import urllib.error
import sys
import argparse
from datetime import datetime

# Notion API config
DATABASE_ID = "b6cee8eb-5431-496b-9bc8-75956bb3ea5d"
API_VERSION = "2026-03-11"

def query_notion_database(api_key, dry_run=False):
    """Query all NPCs from Notion database with pagination."""
    
    url = f"https://api.notion.com/v1/data_sources/{DATABASE_ID}/query"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": API_VERSION,
        "Content-Type": "application/json"
    }
    
    all_results = []
    next_cursor = None
    page_count = 0
    
    print("Querying Notion API...")
    
    while True:
        page_count += 1
        body = {"page_size": 100}
        if next_cursor:
            body["start_cursor"] = next_cursor
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode(),
                headers=headers,
                method="POST"
            )
            
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                results = data.get('results', [])
                all_results.extend(results)
                
                print(f"  Page {page_count}: fetched {len(results)} entries (total: {len(all_results)})")
                
                next_cursor = data.get('next_cursor')
                if not next_cursor:
                    break
                    
        except urllib.error.HTTPError as e:
            error_msg = e.read().decode()
            print(f"ERROR: HTTP {e.code}")
            print(error_msg)
            return None
        except Exception as e:
            print(f"ERROR: {e}")
            return None
    
    print(f"\n✓ Successfully fetched {len(all_results)} NPCs\n")
    return all_results

def extract_npc_data(results):
    """Extract NPC names and properties from Notion results."""
    
    npcs = []
    
    for result in results:
        props = result.get('properties', {})
        
        # Extract name
        name_prop = props.get('Name', {})
        name_text = name_prop.get('title', [])
        name = name_text[0]['plain_text'] if name_text else "UNNAMED"
        
        # Extract other properties
        campaign = props.get('Campaign', {}).get('multi_select', [])
        faction = props.get('Faction', {}).get('multi_select', [])
        location = props.get('Location', {}).get('multi_select', [])
        role = props.get('Role', {}).get('rich_text', [])
        description = props.get('Description', {}).get('rich_text', [])
        transformed_status = props.get('Transformed Status', {}).get('select', {})
        transformed_into = props.get('Transformed Into', {}).get('rich_text', [])
        natural_race = props.get('Natural Race', {}).get('relation', [])
        
        npc_data = {
            'name': name,
            'campaign': [c['name'] for c in campaign],
            'faction': [f['name'] for f in faction],
            'location': [l['name'] for l in location],
            'role': role[0]['plain_text'] if role else '',
            'description': description[0]['plain_text'] if description else '',
            'transformed_status': transformed_status.get('name', '') if isinstance(transformed_status, dict) else '',
            'transformed_into': transformed_into[0]['plain_text'] if transformed_into else '',
            'natural_race': len(natural_race) > 0,
            'has_all_fields': bool(
                name != "UNNAMED" and
                campaign and
                faction and
                location and
                role and
                transformed_status
            )
        }
        
        npcs.append(npc_data)
    
    return sorted(npcs, key=lambda x: x['name'])

def save_results(npcs, output_file, dry_run=False):
    """Save NPC data to JSON and plaintext files."""
    
    if dry_run:
        print("[DRY RUN] Would save to:")
        print(f"  - {output_file}")
        print(f"  - {output_file.replace('.json', '.txt')}")
        print()
        return
    
    # Save JSON
    json_file = output_file
    with open(json_file, 'w') as f:
        json.dump({
            'export_date': datetime.now().isoformat(),
            'total_npcs': len(npcs),
            'npcs': npcs
        }, f, indent=2)
    
    # Save plaintext
    txt_file = output_file.replace('.json', '.txt')
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(f"Aethelmark NPCs Export\n")
        f.write(f"Exported: {datetime.now().isoformat()}\n")
        f.write(f"Total NPCs: {len(npcs)}\n")
        f.write("=" * 80 + "\n\n")
        
        # Fully populated NPCs
        complete = [n for n in npcs if n['has_all_fields']]
        incomplete = [n for n in npcs if not n['has_all_fields']]
        
        f.write(f"COMPLETE ({len(complete)} NPCs):\n")
        f.write("-" * 80 + "\n")
        for npc in complete:
            f.write(f"✓ {npc['name']}\n")
        
        f.write(f"\n\nINCOMPLETE ({len(incomplete)} NPCs - missing fields):\n")
        f.write("-" * 80 + "\n")
        for npc in incomplete:
            missing = []
            if not npc['campaign']: missing.append('campaign')
            if not npc['faction']: missing.append('faction')
            if not npc['location']: missing.append('location')
            if not npc['role']: missing.append('role')
            if not npc['transformed_status']: missing.append('transformed_status')
            f.write(f"✗ {npc['name']} (missing: {', '.join(missing)})\n")
    
    print(f"✓ Saved to {json_file}")
    print(f"✓ Saved to {txt_file}")

def main():
    parser = argparse.ArgumentParser(
        description="Query Notion Aethelmark NPCs database and export list"
    )
    parser.add_argument('--api-key', required=True, help='Notion API key')
    parser.add_argument('--output', default='aethelmark_npcs_export.json', help='Output filename')
    parser.add_argument('--dry-run', action='store_true', help='Preview without saving')
    
    args = parser.parse_args()
    
    # Query database
    results = query_notion_database(args.api_key, args.dry_run)
    if results is None:
        sys.exit(1)
    
    # Extract and process
    npcs = extract_npc_data(results)
    
    # Show summary
    complete = sum(1 for n in npcs if n['has_all_fields'])
    incomplete = len(npcs) - complete
    
    print(f"NPC Data Summary:")
    print(f"  Complete (all fields): {complete}")
    print(f"  Incomplete (missing fields): {incomplete}")
    print()
    
    # Save results
    save_results(npcs, args.output, args.dry_run)

if __name__ == '__main__':
    main()
