
import pytest

@pytest.fixture
def association_headers():
    return ['id', 'predicate', 'category', 'agent_type', 'aggregator_knowledge_source', 'knowledge_level', 'original_predicate', 'primary_knowledge_source', 'file_source', 'provided_by', 'publications', 'qualifiers', 'has_evidence', 'frequency_qualifier', 'has_count', 'has_percentage', 'has_quotient', 'has_total', 'negated', 'onset_qualifier', 'sex_qualifier', 'disease_context_qualifier', 'has_attribute', 'object_aspect_qualifier', 'sources', 'supporting_text', 'species_context_qualifier', 'stage_qualifier', 'qualifier', 'object_specialization_qualifier', 'FDA_adverse_event_level', 'subject', 'object', 'original_subject', 'original_object', 'evidence_count', 'grouping_key', 'subject_label', 'subject_category', 'subject_namespace', 'subject_closure', 'subject_closure_label', 'subject_taxon', 'subject_taxon_label', 'object_label', 'object_category', 'object_namespace', 'object_closure', 'object_closure_label', 'object_taxon', 'object_taxon_label', 'disease_context_qualifier_label', 'disease_context_qualifier_category', 'disease_context_qualifier_namespace', 'disease_context_qualifier_closure', 'disease_context_qualifier_closure_label', 'species_context_qualifier_label', 'species_context_qualifier_category', 'species_context_qualifier_namespace', 'stage_qualifier_label', 'stage_qualifier_category', 'stage_qualifier_namespace', 'sex_qualifier_label', 'sex_qualifier_category', 'sex_qualifier_namespace', 'onset_qualifier_label', 'onset_qualifier_category', 'onset_qualifier_namespace', 'frequency_qualifier_label', 'frequency_qualifier_category', 'frequency_qualifier_namespace', 'highlighting']

@pytest.fixture
def histobin_headers():
    return ['label', 'count', 'id']

@pytest.fixture
def node_headers():
    return ['id', 'category', 'name', 'description', 'xref', 'synonym', 'exact_synonym', 'broad_synonym', 'narrow_synonym', 'related_synonym', 'deprecated', 'in_taxon', 'in_taxon_label', 'iri', 'same_as', 'subsets', 'file_source', 'provided_by', 'full_name', 'symbol', 'has_gene', 'type', 'has_attribute', 'has_biological_sex', 'synonyms', 'namespace', 'has_phenotype', 'has_phenotype_label', 'has_phenotype_count', 'has_phenotype_closure', 'has_phenotype_closure_label', 'has_descendant', 'has_descendant_label', 'has_descendant_count', 'uri', 'inheritance', 'causal_gene', 'causes_disease', 'node_relationships', 'mappings', 'external_links', 'provided_by_link', 'association_counts', 'cross_species_term_clique', 'node_hierarchy']

@pytest.fixture
def search_headers():
    return ['id', 'category', 'name', 'description', 'xref', 'synonym', 'exact_synonym', 'broad_synonym', 'narrow_synonym', 'related_synonym', 'deprecated', 'in_taxon', 'in_taxon_label', 'iri', 'same_as', 'subsets', 'file_source', 'provided_by', 'full_name', 'symbol', 'has_gene', 'type', 'has_attribute', 'has_biological_sex', 'synonyms', 'namespace', 'has_phenotype', 'has_phenotype_label', 'has_phenotype_count', 'has_phenotype_closure', 'has_phenotype_closure_label', 'has_descendant', 'has_descendant_label', 'has_descendant_count', 'score', 'highlighting']
