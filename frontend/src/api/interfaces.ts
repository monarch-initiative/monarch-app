export type NodeId = string
export type InheritanceId = string
export type SynonymId = string
export type TaxonId = string
export type AssociationCountId = string
export interface Node  {
    id?: string,
    label?: string,
    iri?: string,
    category?: string,
    clinical_modifiers?: string,
    replaced_by?: string,
    deprecated?: string,
    consider?: string,
    xrefs?: string,
    synonyms?: Synonym[],
    taxon?: Taxon,
    inheritance?: Inheritance,
    association_counts?: {[index: AssociationCountId]: AssociationCount },
}
export interface Inheritance  {
    id?: string,
    pred?: string,
    xrefs?: string,
}
export interface Synonym  {
    id?: string,
    label?: string,
    iri?: string,
}
export interface Taxon  {
    id?: string,
    label?: string,
}
export interface AssociationCount  {
    id?: string,
    counts?: string,
    counts_by_taxon?: string,
}
