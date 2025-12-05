#!/usr/bin/env python3
"""
GFF Statistics Generator

Processes a GFF file and generates statistics including:
- Total number of features
- Count by feature type
- Average length by type
- Strand distribution
"""

import argparse
import json
from collections import defaultdict
from pathlib import Path


def parse_gff_line(line):
    """
    Parse a single GFF line.
    
    Returns a dictionary with GFF fields or None if line is a comment.
    GFF format: seqname, source, feature, start, end, score, strand, frame, attributes
    """
    line = line.strip()
    
    # Skip empty lines and comments
    if not line or line.startswith('#'):
        return None
    
    fields = line.split('\t')
    if len(fields) < 8:
        return None
    
    return {
        'seqname': fields[0],
        'source': fields[1],
        'feature': fields[2],
        'start': int(fields[3]),
        'end': int(fields[4]),
        'score': fields[5],
        'strand': fields[6],
        'frame': fields[7],
        'attributes': fields[8] if len(fields) > 8 else ''
    }


def calculate_length(feature):
    """Calculate the length of a feature based on start and end positions."""
    return feature['end'] - feature['start'] + 1


def process_gff(gff_file, filter_type=None):
    """
    Process a GFF file and calculate statistics.
    
    Args:
        gff_file: Path to the GFF file
        filter_type: Optional feature type to filter by
    
    Returns:
        Dictionary with calculated statistics
    """
    features = []
    
    # Parse the GFF file
    with open(gff_file, 'r') as f:
        for line in f:
            parsed = parse_gff_line(line)
            if parsed:
                # Apply filter if specified
                if filter_type is None or parsed['feature'] == filter_type:
                    features.append(parsed)
    
    # Calculate statistics
    total_features = len(features)
    
    # Count by type
    by_type = defaultdict(int)
    for feature in features:
        by_type[feature['feature']] += 1
    
    # Average length by type
    avg_length = {}
    lengths_by_type = defaultdict(list)
    
    for feature in features:
        length = calculate_length(feature)
        lengths_by_type[feature['feature']].append(length)
    
    for feature_type, lengths in lengths_by_type.items():
        avg_length[feature_type] = round(sum(lengths) / len(lengths), 1)
    
    # Strand distribution
    strand_distribution = defaultdict(int)
    for feature in features:
        strand_distribution[feature['strand']] += 1
    
    # Build result dictionary
    result = {
        'total_features': total_features,
        'by_type': dict(by_type),
        'avg_length': avg_length,
        'strand_distribution': dict(strand_distribution)
    }
    
    return result


def main():
    """Main function to parse arguments and run the program."""
    parser = argparse.ArgumentParser(
        description='Calculate statistics from a GFF file'
    )
    parser.add_argument(
        '--gff',
        required=True,
        type=str,
        help='Path to the GFF file'
    )
    parser.add_argument(
        '--out',
        required=True,
        type=str,
        help='Output JSON file path'
    )
    parser.add_argument(
        '--filter-type',
        type=str,
        default=None,
        help='Filter by feature type (optional)'
    )
    
    args = parser.parse_args()
    
    # Check if GFF file exists
    gff_path = Path(args.gff)
    if not gff_path.exists():
        raise FileNotFoundError(f"GFF file not found: {args.gff}")
    
    # Process the GFF file
    stats = process_gff(str(gff_path), filter_type=args.filter_type)
    
    # Write output to JSON
    output_path = Path(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"Statistics written to {output_path}")


if __name__ == '__main__':
    main()
