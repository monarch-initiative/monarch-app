
import pytest

@pytest.fixture
def association_headers():
    return ['id', 'category', 'subject', 'original_subject', 'subject_namespace', 'subject_category', 'subject_closure', 'subject_label', 'subject_closure_label', 'subject_taxon', 'subject_taxon_label', 'predicate', 'original_predicate', 'object', 'original_object', 'object_namespace', 'object_category', 'object_closure', 'object_label', 'object_closure_label', 'object_taxon', 'object_taxon_label', 'primary_knowledge_source', 'aggregator_knowledge_source', 'negated', 'pathway', 'evidence_count', 'knowledge_level', 'agent_type', 'has_evidence', 'has_evidence_links', 'has_count', 'has_total', 'has_percentage', 'has_quotient', 'grouping_key', 'provided_by', 'provided_by_link', 'publications', 'publications_links', 'frequency_qualifier', 'onset_qualifier', 'sex_qualifier', 'stage_qualifier', 'qualifiers', 'qualifiers_label', 'qualifiers_namespace', 'qualifiers_category', 'qualifier', 'qualifier_label', 'qualifier_namespace', 'qualifier_category', 'frequency_qualifier_label', 'frequency_qualifier_namespace', 'frequency_qualifier_category', 'onset_qualifier_label', 'onset_qualifier_namespace', 'onset_qualifier_category', 'sex_qualifier_label', 'sex_qualifier_namespace', 'sex_qualifier_category', 'stage_qualifier_label', 'stage_qualifier_namespace', 'stage_qualifier_category', 'disease_context_qualifier', 'disease_context_qualifier_label', 'disease_context_qualifier_namespace', 'disease_context_qualifier_category', 'disease_context_qualifier_closure', 'disease_context_qualifier_closure_label', 'species_context_qualifier', 'species_context_qualifier_label', 'species_context_qualifier_namespace', 'species_context_qualifier_category', 'subject_specialization_qualifier', 'subject_specialization_qualifier_label', 'subject_specialization_qualifier_namespace', 'subject_specialization_qualifier_category', 'subject_specialization_qualifier_closure', 'subject_specialization_qualifier_closure_label', 'object_specialization_qualifier', 'object_specialization_qualifier_label', 'object_specialization_qualifier_namespace', 'object_specialization_qualifier_category', 'object_specialization_qualifier_closure', 'object_specialization_qualifier_closure_label', 'highlighting']

@pytest.fixture
def histobin_headers():
    return ['label', 'count', 'id']

@pytest.fixture
def node_headers():
    return ['id', 'category', 'name', 'full_name', 'deprecated', 'description', 'xref', 'provided_by', 'in_taxon', 'in_taxon_label', 'symbol', 'synonym', 'broad_synonym', 'exact_synonym', 'narrow_synonym', 'related_synonym', 'subsets', 'uri', 'iri', 'namespace', 'has_phenotype', 'has_phenotype_label', 'has_phenotype_closure', 'has_phenotype_closure_label', 'has_phenotype_count', 'has_descendant', 'has_descendant_label', 'has_descendant_count', 'inheritance', 'causal_gene', 'causes_disease', 'mappings', 'external_links', 'provided_by_link', 'association_counts', 'node_hierarchy']

@pytest.fixture
def search_headers():
    return ['id', 'category', 'name', 'full_name', 'deprecated', 'description', 'xref', 'provided_by', 'in_taxon', 'in_taxon_label', 'symbol', 'synonym', 'broad_synonym', 'exact_synonym', 'narrow_synonym', 'related_synonym', 'subsets', 'uri', 'iri', 'namespace', 'has_phenotype', 'has_phenotype_label', 'has_phenotype_closure', 'has_phenotype_closure_label', 'has_phenotype_count', 'has_descendant', 'has_descendant_label', 'has_descendant_count', 'score', 'highlighting']
