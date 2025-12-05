#!/usr/bin/env python3
"""
Test suite for gff_stats.py (without pytest dependency)

Tests include:
- Unit tests with asserts for individual functions
- Integration tests with actual GFF file
- Edge cases and error handling
"""

import json
import tempfile
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from gff_stats import parse_gff_line, calculate_length, process_gff


# ==================== Test Helpers ====================

test_count = 0
passed_count = 0
failed_count = 0


def assert_equal(actual, expected, msg=""):
    """Assert that actual equals expected."""
    if actual != expected:
        raise AssertionError(f"Expected {expected}, got {actual}. {msg}")


def assert_true(condition, msg=""):
    """Assert that condition is True."""
    if not condition:
        raise AssertionError(f"Assertion failed: {msg}")


def assert_is_none(value, msg=""):
    """Assert that value is None."""
    if value is not None:
        raise AssertionError(f"Expected None, got {value}. {msg}")


def assert_is_not_none(value, msg=""):
    """Assert that value is not None."""
    if value is None:
        raise AssertionError(f"Expected non-None value. {msg}")


def assert_in(item, container, msg=""):
    """Assert that item is in container."""
    if item not in container:
        raise AssertionError(f"{item} not in {container}. {msg}")


def assert_greater(actual, threshold, msg=""):
    """Assert that actual > threshold."""
    if actual <= threshold:
        raise AssertionError(f"Expected > {threshold}, got {actual}. {msg}")


def run_test(test_func, test_name):
    """Run a test function and track results."""
    global test_count, passed_count, failed_count
    test_count += 1
    try:
        test_func()
        print(f"✓ {test_name}")
        passed_count += 1
    except Exception as e:
        print(f"✗ {test_name}")
        print(f"  Error: {e}")
        failed_count += 1


# ==================== Unit Tests ====================

def test_parse_gff_line_valid():
    """Test parsing a valid GFF line."""
    gff_line = "NC_000908.2\tRefSeq\tgene\t1\t107\t.\t+\t.\tID=gene-MG_0001"
    parsed = parse_gff_line(gff_line)
    
    assert_is_not_none(parsed)
    assert_equal(parsed['seqname'], 'NC_000908.2')
    assert_equal(parsed['source'], 'RefSeq')
    assert_equal(parsed['feature'], 'gene')
    assert_equal(parsed['start'], 1)
    assert_equal(parsed['end'], 107)
    assert_equal(parsed['strand'], '+')
    assert_equal(parsed['frame'], '.')


def test_parse_gff_line_comment():
    """Test that comment lines return None."""
    gff_line = "##gff-version 3"
    parsed = parse_gff_line(gff_line)
    assert_is_none(parsed)


def test_parse_gff_line_empty():
    """Test that empty lines return None."""
    parsed = parse_gff_line("")
    assert_is_none(parsed)


def test_parse_gff_line_incomplete():
    """Test that incomplete lines return None."""
    gff_line = "NC_000908.2\tRefSeq\tgene"  # Only 3 fields, needs at least 8
    parsed = parse_gff_line(gff_line)
    assert_is_none(parsed)


def test_parse_gff_line_with_whitespace():
    """Test parsing with leading/trailing whitespace."""
    gff_line = "  NC_000908.2\tRefSeq\tCDS\t124\t202\t.\t+\t0\tID=cds-MG_0002  "
    parsed = parse_gff_line(gff_line)
    
    assert_is_not_none(parsed)
    assert_equal(parsed['feature'], 'CDS')
    assert_equal(parsed['start'], 124)


def test_calculate_length():
    """Test length calculation."""
    feature = {'start': 1, 'end': 107}
    length = calculate_length(feature)
    assert_equal(length, 107)


def test_calculate_length_single_base():
    """Test length calculation for single base."""
    feature = {'start': 100, 'end': 100}
    length = calculate_length(feature)
    assert_equal(length, 1)


def test_calculate_length_large_feature():
    """Test length calculation for large feature."""
    feature = {'start': 1, 'end': 580076}
    length = calculate_length(feature)
    assert_equal(length, 580076)


# ==================== Integration Tests ====================

def test_process_gff_full():
    """Test processing a real GFF file (mycoplasma)."""
    gff_file = Path(__file__).parent.parent / "Data" / "gff mycoplasma"
    
    if gff_file.exists():
        stats = process_gff(str(gff_file))
        
        # Verify structure
        assert_in('total_features', stats)
        assert_in('by_type', stats)
        assert_in('avg_length', stats)
        assert_in('strand_distribution', stats)
        
        # Verify data types
        assert_true(isinstance(stats['total_features'], int), "total_features should be int")
        assert_true(isinstance(stats['by_type'], dict), "by_type should be dict")
        assert_true(isinstance(stats['avg_length'], dict), "avg_length should be dict")
        assert_true(isinstance(stats['strand_distribution'], dict), "strand_distribution should be dict")
        
        # Verify values
        assert_greater(stats['total_features'], 0, "Should have features")
        assert_in('gene', stats['by_type'])
        assert_in('CDS', stats['by_type'])
        assert_greater(stats['by_type']['gene'], 0, "Should have genes")


def test_process_gff_with_filter():
    """Test processing with filter_type parameter."""
    gff_file = Path(__file__).parent.parent / "Data" / "gff mycoplasma"
    
    if gff_file.exists():
        stats_filtered = process_gff(str(gff_file), filter_type='CDS')
        
        # Verify only CDS type exists in by_type
        assert_in('CDS', stats_filtered['by_type'])
        assert_greater(stats_filtered['by_type']['CDS'], 0)
        
        # Total should equal CDS count (only CDS was processed)
        assert_equal(stats_filtered['total_features'], stats_filtered['by_type']['CDS'])


def test_process_gff_strand_distribution():
    """Test strand distribution."""
    gff_file = Path(__file__).parent.parent / "Data" / "gff mycoplasma"
    
    if gff_file.exists():
        stats = process_gff(str(gff_file))
        
        # Verify strand distribution exists
        strand_sum = sum(stats['strand_distribution'].values())
        assert_greater(strand_sum, 0)
        assert_in('+', stats['strand_distribution'])
        assert_in('-', stats['strand_distribution'])


def test_process_gff_avg_length_reasonable():
    """Test that average lengths are reasonable."""
    gff_file = Path(__file__).parent.parent / "Data" / "gff mycoplasma"
    
    if gff_file.exists():
        stats = process_gff(str(gff_file))
        
        # All average lengths should be positive
        for feature_type, avg_len in stats['avg_length'].items():
            assert_greater(avg_len, 0, f"avg_length[{feature_type}] should be positive")
            assert_true(isinstance(avg_len, float), f"avg_length should be float")


# ==================== Edge Cases ====================

def test_process_empty_gff():
    """Test processing an empty GFF file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gff', delete=False) as f:
        f.write("")
        temp_path = f.name
    
    try:
        stats = process_gff(temp_path)
        assert_equal(stats['total_features'], 0)
        assert_equal(stats['by_type'], {})
        assert_equal(stats['avg_length'], {})
        assert_equal(stats['strand_distribution'], {})
    finally:
        Path(temp_path).unlink()


def test_process_only_comments_gff():
    """Test processing a GFF file with only comments."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gff', delete=False) as f:
        f.write("##gff-version 3\n")
        f.write("##sequence-region NC_000001 1 1000\n")
        temp_path = f.name
    
    try:
        stats = process_gff(temp_path)
        assert_equal(stats['total_features'], 0)
        assert_equal(stats['by_type'], {})
    finally:
        Path(temp_path).unlink()


def test_process_single_feature_gff():
    """Test processing a GFF file with a single feature."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gff', delete=False) as f:
        f.write("NC_000001\ttest\tgene\t100\t200\t.\t+\t.\tID=test1\n")
        temp_path = f.name
    
    try:
        stats = process_gff(temp_path)
        assert_equal(stats['total_features'], 1)
        assert_equal(stats['by_type']['gene'], 1)
        assert_equal(stats['avg_length']['gene'], 101.0)
        assert_equal(stats['strand_distribution']['+'], 1)
    finally:
        Path(temp_path).unlink()


def test_process_multiple_strands_gff():
    """Test processing a GFF file with multiple strands."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gff', delete=False) as f:
        f.write("NC_000001\ttest\tgene\t100\t200\t.\t+\t.\tID=test1\n")
        f.write("NC_000001\ttest\tgene\t300\t400\t.\t-\t.\tID=test2\n")
        f.write("NC_000001\ttest\tCDS\t100\t150\t.\t+\t0\tID=test3\n")
        temp_path = f.name
    
    try:
        stats = process_gff(temp_path)
        assert_equal(stats['total_features'], 3)
        assert_equal(stats['strand_distribution']['+'], 2)
        assert_equal(stats['strand_distribution']['-'], 1)
    finally:
        Path(temp_path).unlink()


def test_process_nonexistent_file():
    """Test that nonexistent file raises FileNotFoundError."""
    try:
        process_gff("/nonexistent/path/file.gff")
        raise AssertionError("Should have raised FileNotFoundError")
    except FileNotFoundError:
        pass  # Expected


# ==================== Data Structure Tests ====================

def test_avg_length_precision():
    """Test that average length is rounded to 1 decimal place."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.gff', delete=False) as f:
        # Create three genes with different lengths
        f.write("NC_000001\ttest\tgene\t1\t10\t.\t+\t.\tID=g1\n")      # length: 10
        f.write("NC_000001\ttest\tgene\t20\t29\t.\t+\t.\tID=g2\n")     # length: 10
        f.write("NC_000001\ttest\tgene\t40\t44\t.\t+\t.\tID=g3\n")     # length: 5
        # Average: (10 + 10 + 5) / 3 = 8.333... -> rounds to 8.3
        temp_path = f.name
    
    try:
        stats = process_gff(temp_path)
        avg = stats['avg_length']['gene']
        # Check it's a float with max 1 decimal place
        assert_true(isinstance(avg, float))
        assert_equal(avg, round(avg, 1))
    finally:
        Path(temp_path).unlink()


# ==================== Consistency Tests ====================

def test_consistency_filtered_vs_unfiltered():
    """Test that filtering produces consistent results."""
    gff_file = Path(__file__).parent.parent / "Data" / "gff mycoplasma"
    
    if gff_file.exists():
        stats_all = process_gff(str(gff_file))
        stats_cds = process_gff(str(gff_file), filter_type='CDS')
        
        # CDS count in filtered should match CDS count in unfiltered
        assert_equal(stats_cds['by_type']['CDS'], stats_all['by_type']['CDS'])
        
        # CDS average length should be the same
        assert_equal(stats_cds['avg_length']['CDS'], stats_all['avg_length']['CDS'])


# ==================== Main Test Runner ====================

if __name__ == '__main__':
    print("=" * 60)
    print("Running GFF Statistics Tests")
    print("=" * 60)
    
    # Unit tests
    print("\n--- Unit Tests ---")
    run_test(test_parse_gff_line_valid, "parse_gff_line: valid GFF line")
    run_test(test_parse_gff_line_comment, "parse_gff_line: comment line")
    run_test(test_parse_gff_line_empty, "parse_gff_line: empty line")
    run_test(test_parse_gff_line_incomplete, "parse_gff_line: incomplete line")
    run_test(test_parse_gff_line_with_whitespace, "parse_gff_line: with whitespace")
    run_test(test_calculate_length, "calculate_length: normal feature")
    run_test(test_calculate_length_single_base, "calculate_length: single base")
    run_test(test_calculate_length_large_feature, "calculate_length: large feature")
    
    # Integration tests
    print("\n--- Integration Tests ---")
    run_test(test_process_gff_full, "process_gff: full mycoplasma file")
    run_test(test_process_gff_with_filter, "process_gff: with filter_type")
    run_test(test_process_gff_strand_distribution, "process_gff: strand distribution")
    run_test(test_process_gff_avg_length_reasonable, "process_gff: avg length reasonable")
    
    # Edge cases
    print("\n--- Edge Cases ---")
    run_test(test_process_empty_gff, "edge case: empty GFF file")
    run_test(test_process_only_comments_gff, "edge case: only comments")
    run_test(test_process_single_feature_gff, "edge case: single feature")
    run_test(test_process_multiple_strands_gff, "edge case: multiple strands")
    run_test(test_process_nonexistent_file, "edge case: nonexistent file")
    
    # Data structure tests
    print("\n--- Data Structure Tests ---")
    run_test(test_avg_length_precision, "avg_length precision: 1 decimal place")
    
    # Consistency tests
    print("\n--- Consistency Tests ---")
    run_test(test_consistency_filtered_vs_unfiltered, "filtered vs unfiltered consistency")
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Tests run: {test_count}")
    print(f"Passed:    {passed_count} ✓")
    print(f"Failed:    {failed_count} ✗")
    print("=" * 60)
    
    # Exit with error code if any tests failed
    sys.exit(0 if failed_count == 0 else 1)
