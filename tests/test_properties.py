import pytest
from hypothesis import given, strategies as st
from runtime.taxonomy.schema.spec import SampleTaxonomy

@given(
    conf1=st.floats(min_value=0.0, max_value=1.0),
    conf2=st.floats(min_value=0.0, max_value=1.0)
)
def test_sample_taxonomy_merge_confidence(conf1, conf2):
    """Property: Merged taxonomy confidence is always the minimum of the two."""
    t1 = SampleTaxonomy(labels={"domain": "web"}, confidence=conf1)
    t2 = SampleTaxonomy(labels={"domain": "binary"}, confidence=conf2)
    
    merged = t1.merge(t2)
    assert merged.confidence == min(conf1, conf2)
    # The source label for the merged object should always be 'merged'
    assert merged.source == "merged"

@given(
    val1=st.text(min_size=1, max_size=10),
    val2=st.text(min_size=1, max_size=10),
    val3=st.text(min_size=1, max_size=10)
)
def test_sample_taxonomy_merge_lists(val1, val2, val3):
    """Property: Merging identical keys containing lists correctly concats them natively."""
    t1 = SampleTaxonomy(labels={"capability": [val1]})
    t2 = SampleTaxonomy(labels={"capability": [val2, val3]})
    
    merged = t1.merge(t2)
    # Since they are lists, the merge func (which uses set intersection) should combine them without duplicates
    assert set(merged.labels["capability"]) == {val1, val2, val3}
