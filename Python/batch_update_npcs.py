# name: Batch Update Aethelmark NPCs
# keywords: [notion, batch, update, npc, automation]
# description: Batch update all incomplete NPCs with campaign, faction, role, and transformed_status
#
# Queries Notion database for each incomplete NPC and updates missing fields based on location and campaign knowledge.
# Uses Notion API to find page IDs and perform updates.
#
# Command line arguments:
#   --api-key KEY: Notion API key (required)
#   --dry-run: Preview updates without applying them

import json
import urllib.request
import urllib.error
import sys
import argparse
from datetime import datetime
import time

DATABASE_ID = "b6cee8eb-5431-496b-9bc8-75956bb3ea5d"
API_VERSION = "2026-03-11"

def fetch_all_npcs_with_ids(api_key):
    """Fetch all NPCs with their page IDs."""
    url = f"https://api.notion.com/v1/data_sources/{DATABASE_ID}/query"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": API_VERSION,
        "Content-Type": "application/json"
    }
    
    all_results = []
    next_cursor = None
    
    print("Fetching all NPCs with page IDs...")
    
    while True:
        body = {"page_size": 100}
        if next_cursor:
            body["start_cursor"] = next_cursor
        
        try:
            req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="POST")
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                results = data.get('results', [])
                all_results.extend(results)
                next_cursor = data.get('next_cursor')
                if not next_cursor:
                    break
        except Exception as e:
            print(f"ERROR fetching NPCs: {e}")
            return None
        
        time.sleep(0.2)
    
    # Build name -> page_id mapping
    npc_map = {}
    for result in all_results:
        name_prop = result.get('properties', {}).get('Name', {}).get('title', [])
        if name_prop:
            name = name_prop[0]['plain_text']
            npc_map[name] = result['id']
    
    print(f"Fetched {len(npc_map)} NPCs\n")
    return npc_map

# NPC update mapping: based on location and campaign knowledge
NPC_UPDATES = {
    "Aldren": {"campaign": "Unaffiliated", "faction": "Unaffiliated", "role": "TBD", "transformed_status": "Not Transformed"},
    "Aldus Corvel": {"campaign": "Viktor Steinfeld", "faction": "Unaffiliated"},
    "Aubert": {"campaign": "Camp Rochevaux", "faction": "Regional", "role": "Camp resident", "transformed_status": "Not Transformed"},
    "Celine Daubray": {"campaign": "Camp Rochevaux", "faction": "Regional", "role": "Camp resident", "transformed_status": "Not Transformed"},
    "Constable Ferris": {"campaign": "Nobles Commission", "faction": "Guilds", "role": "Constable", "transformed_status": "Not Transformed"},
    "Corvel": {"faction": "Merchant Families"},
    "Dietrich Haan": {"campaign": "Nobles Commission", "faction": "Unaffiliated", "role": "Town resident", "transformed_status": "Not Transformed"},
    "Duval": {"campaign": "Camp Rochevaux", "faction": "Regional", "role": "Camp resident", "transformed_status": "Not Transformed"},
    "Edouard Vellancourt": {"campaign": "Maruvec Campaign", "faction": "Noble Houses", "role": "Comte patron - founder of Kennel Hounds Programme", "transformed_status": "Not Transformed"},
    "Elise Marenne": {"campaign": "Vauclair", "faction": "Regional", "role": "Town resident", "transformed_status": "Not Transformed"},
    "Emperor Aldric": {"campaign": "Nobles Commission", "faction": "Noble Houses", "role": "Fertility appointment (24 Apr)", "transformed_status": "Not Transformed"},
    "Fabron": {"campaign": "Camp Rochevaux", "faction": "Regional", "role": "Camp resident", "transformed_status": "Not Transformed"},
    "Fenk": {"campaign": "Nobles Commission", "faction": "Unaffiliated", "role": "Town resident", "transformed_status": "Not Transformed"},
    "Gate Man": {"campaign": "Camp Rochevaux", "faction": "Regional", "role": "Gate keeper", "transformed_status": "Not Transformed"},
    "Gervais Tournon": {"campaign": "Camp Rochevaux", "faction": "Regional", "role": "Camp resident", "transformed_status": "Not Transformed"},
    "Gregor": {"campaign": "Camp Rochevaux", "faction": "Regional", "role": "Camp resident", "transformed_status": "Not Transformed"},
    "Grenn": {"campaign": "Camp Rochevaux", "faction": "Regional", "role": "Camp resident", "transformed_status": "Not Transformed"},
    "Halden Creuse": {"campaign": "Camp Rochevaux", "faction": "Regional", "role": "Camp resident", "transformed_status": "Not Transformed"},
    "Joren": {"campaign": "Camp Rochevaux", "faction": "Regional", "role": "Camp resident", "transformed_status": "Not Transformed"},
    "Judge Thomas Kinsky": {"campaign": "Nobles Commission", "faction": "Guilds", "role": "Judge - legal hearing (est. ~2 May)", "transformed_status": "Not Transformed"},
    "Kaz Quickclaw": {"campaign": "Maruvec Campaign", "faction": "Kennel Hounds Program", "role": "Quickclaw family", "transformed_status": "Not Transformed"},
    "Kess": {"campaign": "Maruvec Campaign", "faction": "Kennel Hounds Program", "role": "Maruvec staff", "transformed_status": "Not Transformed"},
    "Lenne Souchard": {"campaign": "Camp Rochevaux", "faction": "Regional", "role": "Camp resident", "transformed_status": "Not Transformed"},
    "Maret Aldec": {"campaign": "Maruvec Campaign", "faction": "Kennel Hounds Program", "role": "Emotional reunion with Sable during harness fitting", "transformed_status": "Not Transformed"},
    "Mathis Renard": {"campaign": "Camp Rochevaux", "faction": "Regional", "role": "Camp resident", "transformed_status": "Not Transformed"},
    "Perret": {"campaign": "Camp Rochevaux", "faction": "Regional", "role": "Camp resident", "transformed_status": "Not Transformed"},
    "Pol": {"campaign": "Nobles Commission", "faction": "Unaffiliated", "role": "Town resident", "transformed_status": "Not Transformed"},
    "Renaud Bastier": {"campaign": "Vauclair", "faction": "Regional", "role": "Town resident", "transformed_status": "Not Transformed"},
    "Renne": {"campaign": "Maruvec Campaign", "faction": "Kennel Hounds Program", "role": "Maruvec staff", "transformed_status": "Not Transformed"},
    "Rill Sunclaw": {"campaign": "Camp Rochevaux", "faction": "Regional", "role": "Camp resident", "transformed_status": "Not Transformed"},
    "Sekkel": {"campaign": "Vauclair", "faction": "Regional", "role": "Town resident", "transformed_status": "Not Transformed"},
    "Silas Drouet": {"campaign": "Maruvec Campaign", "faction": "Kennel Hounds Program", "role": "Maruvec staff", "transformed_status": "Not Transformed"},
    "Tessier": {"campaign": "Camp Rochevaux", "faction": "Regional", "role": "Camp resident", "transformed_status": "Not Transformed"},
    "The Buyer": {"campaign": "Camp Rochevaux", "faction": "Merchant Families", "role": "Buyer - facility owner", "transformed_status": "Not Transformed"},
    "Varne": {"campaign": "Vauclair", "faction": "Regional", "role": "Town resident", "transformed_status": "Not Transformed"},
    "Voss and Kraemer": {"campaign": "Viktor Steinfeld", "faction": "Noble Houses", "role": "Estate staff", "transformed_status": "Not Transformed"},
    "Yara Quickclaw": {"campaign": "Maruvec Campaign", "faction": "Kennel Hounds Program", "role": "Quickclaw family", "transformed_status": "Not Transformed"},
}

def update_npc(api_key, page_id, updates, dry_run=False):
    """Update NPC properties."""
    if dry_run:
        return True
    
    url = f"https://api.notion.com/v1/pages/{page_id}"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Notion-Version": API_VERSION,
        "Content-Type": "application/json"
    }
    
    # Build property updates
    properties = {}
    
    if "campaign" in updates:
        properties["Campaign"] = {
            "multi_select": [{"name": updates["campaign"]}]
        }
    
    if "faction" in updates:
        properties["Faction"] = {
            "multi_select": [{"name": updates["faction"]}]
        }
    
    if "role" in updates:
        properties["Role"] = {
            "rich_text": [{"text": {"content": updates["role"]}}]
        }
    
    if "transformed_status" in updates:
        properties["Transformed Status"] = {
            "select": {"name": updates["transformed_status"]}
        }
    
    body = {"properties": properties}
    
    try:
        req = urllib.request.Request(url, data=json.dumps(body).encode(), headers=headers, method="PATCH")
        with urllib.request.urlopen(req) as response:
            json.loads(response.read().decode())
            return True
    except Exception as e:
        print(f"  ✗ Update failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Batch update incomplete NPCs")
    parser.add_argument('--api-key', required=True, help='Notion API key')
    parser.add_argument('--dry-run', action='store_true', help='Preview without updating')
    
    args = parser.parse_args()
    
    # Fetch NPC data with page IDs
    npc_map = fetch_all_npcs_with_ids(args.api_key)
    if not npc_map:
        sys.exit(1)
    
    print("Batch Updating Aethelmark NPCs")
    print("=" * 80)
    print(f"Total NPCs to update: {len(NPC_UPDATES)}\n")
    
    if args.dry_run:
        print("[DRY RUN MODE]\n")
    
    successful = 0
    failed = 0
    skipped = 0
    
    for npc_name, updates in sorted(NPC_UPDATES.items()):
        print(f"Processing: {npc_name}...", end=" ")
        
        # Get page ID
        if npc_name not in npc_map:
            print("✗ NOT FOUND")
            failed += 1
            continue
        
        page_id = npc_map[npc_name]
        
        # Update NPC
        if update_npc(args.api_key, page_id, updates, args.dry_run):
            print("✓")
            successful += 1
        else:
            failed += 1
        
        time.sleep(0.5)  # Rate limit (3 req/sec = 333ms min)
    
    print("\n" + "=" * 80)
    print(f"Results: {successful} updated, {failed} failed")
    
    if args.dry_run:
        print("\n[DRY RUN] No changes were applied.")

if __name__ == '__main__':
    main()
