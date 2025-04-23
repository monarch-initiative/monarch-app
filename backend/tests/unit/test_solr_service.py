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


def test_strip_excluded_fields():
    # Input document
    doc = {
        "id": "123",
        "name_t": "example name",
        "description_t": "example description",
        "_version_": 1,
        "iri": "http://example.com",
        "frequency_computed_sortable_float": 0.5,
        "has_quotient_sortable_float": 0.3,
        "has_percentage_sortable_float": 0.7,
    }

    # Expected stripped document
    expected = {
        "id": "123",
    }

    # Call the method
    SolrService._strip_excluded_fields(doc)

    # Assert the result matches the expected output
    assert doc == expected


def test_strip_json():
    # Input document
    doc = {
        "id": "123",
        "name": "example name",
        "_version_": 1,
        "iri": "http://example.com",
    }

    # Expected stripped document
    expected = {
        "id": "123",
        "name": "example name",
    }

    # Call the method
    SolrService._strip_json(doc, "_version_", "iri")

    # Assert the result matches the expected output
    assert doc == expected


def test_strip_json_by_suffix():
    # Input document
    doc = {
        "id": "123",
        "name_t": "example name",
        "description_t": "example description",
        "name": "example name",
    }

    # Expected stripped document
    expected = {
        "id": "123",
        "name": "example name",
    }

    # Call the method
    SolrService._strip_json_by_suffix(doc, "_t")

    # Assert the result matches the expected output
    assert doc == expected
