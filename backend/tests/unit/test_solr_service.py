from monarch_py.service.solr_service import SolrService, FIELD_TYPE_SUFFIXES


def test_consolidate_highlights():
    # Input highlights
    highlights = {
        "MONDO:123": {
            "name_t": ["<em>example</em> name", "another <em>example</em>"],
            "description_t": ["<em>example</em> description"],
            "name_ac": ["a third <em>example</em> name"],
        },
        "HGNC:456": {
            "name_t": ["<em>heart</em> gene"],
            "description_t": ["gene description about <em>heart</em>"],
            "name_ac": ["<em>heart</em> gene"],
        },
    }

    # Expected consolidated highlights
    expected = {
        "MONDO:123": {
            "name": ["<em>example</em> name", "a third <em>example</em> name", "another <em>example</em>"],
            "description": ["<em>example</em> description"],
        },
        "HGNC:456": {
            "name": ["<em>heart</em> gene"],
            "description": ["gene description about <em>heart</em>"],
        },
    }

    # Call the method
    result = SolrService._consolidate_highlights(highlights, FIELD_TYPE_SUFFIXES)

    # Assert the result matches the expected output
    assert result == expected
