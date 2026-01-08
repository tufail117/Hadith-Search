"""Convert GitHub JSON format to unified hadith schema."""

import json
from pathlib import Path
from typing import List, Dict, Any


def convert_hadith(hadith: Dict[str, Any], book_name: str, chapter_english: str) -> Dict[str, Any]:
    """
    Convert a single hadith from GitHub format to unified schema.

    Args:
        hadith: Hadith dict from GitHub JSON
        book_name: 'bukhari' or 'muslim'
        chapter_english: Chapter name in English

    Returns:
        Hadith in unified schema format
    """
    english = hadith.get('english', {})
    narrator = english.get('narrator', '').strip()
    text = english.get('text', '').strip()

    # Create full_text for search (narrator + text)
    full_text = f"{narrator} {text}".strip()

    # Generate unique ID using book + chapter + hadith number
    book_id = hadith.get('bookId', 1)
    chapter_id = hadith.get('chapterId', 0)
    hadith_num = hadith.get('idInBook', hadith.get('id', 0))
    hadith_id = f"{book_name}_{book_id}_{chapter_id}_{hadith_num}"

    return {
        "id": hadith_id,
        "book": book_name,
        "volume": hadith.get('bookId', 1),
        "chapter": chapter_english,
        "hadith_number": hadith.get('idInBook', hadith.get('id')),
        "narrator": narrator,
        "text": text,
        "full_text": full_text
    }


def convert_json_file(json_path: Path, book_name: str) -> List[Dict[str, Any]]:
    """
    Convert a single JSON file to unified format.

    Args:
        json_path: Path to JSON file
        book_name: 'bukhari' or 'muslim'

    Returns:
        List of hadiths in unified format
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Get chapter information
    chapter = data.get('chapter', {})
    chapter_english = chapter.get('english', 'Unknown')

    # Convert all hadiths in this file
    hadiths = []
    for hadith in data.get('hadiths', []):
        converted = convert_hadith(hadith, book_name, chapter_english)
        hadiths.append(converted)

    return hadiths


def convert_all_json(bukhari_dir: Path, muslim_dir: Path) -> List[Dict[str, Any]]:
    """
    Convert all JSON files from both collections.

    Args:
        bukhari_dir: Directory containing Bukhari JSON files
        muslim_dir: Directory containing Muslim JSON files

    Returns:
        List of all hadiths in unified format
    """
    all_hadiths = []

    # Process Bukhari
    print("Converting Bukhari hadiths...")
    bukhari_files = sorted(bukhari_dir.glob('*.json'))
    for json_file in bukhari_files:
        hadiths = convert_json_file(json_file, 'bukhari')
        all_hadiths.extend(hadiths)
        print(f"  {json_file.name}: {len(hadiths)} hadiths")

    print(f"Bukhari total: {len([h for h in all_hadiths if h['book'] == 'bukhari'])} hadiths")

    # Process Muslim
    print("\nConverting Muslim hadiths...")
    muslim_files = sorted(muslim_dir.glob('*.json'))
    for json_file in muslim_files:
        hadiths = convert_json_file(json_file, 'muslim')
        all_hadiths.extend(hadiths)
        print(f"  {json_file.name}: {len(hadiths)} hadiths")

    print(f"Muslim total: {len([h for h in all_hadiths if h['book'] == 'muslim'])} hadiths")
    print(f"\nGrand total: {len(all_hadiths)} hadiths")

    return all_hadiths


def save_hadiths(hadiths: List[Dict[str, Any]], output_path: Path) -> None:
    """
    Save hadiths to JSON file.

    Args:
        hadiths: List of hadiths in unified format
        output_path: Path to output JSON file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(hadiths, f, ensure_ascii=False, indent=2)

    print(f"\nSaved {len(hadiths)} hadiths to {output_path}")


if __name__ == "__main__":
    # Test conversion
    from src.config import BUKHARI_DIR, MUSLIM_DIR, HADITHS_JSON

    hadiths = convert_all_json(BUKHARI_DIR, MUSLIM_DIR)
    save_hadiths(hadiths, HADITHS_JSON)
