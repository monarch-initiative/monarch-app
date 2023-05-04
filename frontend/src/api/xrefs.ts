import { isAbsolute } from "@/util/url";

/** external references */

/** get url/link from identifier */
export const getXrefLink = (identifier: string): string => {
  /** if already a url, just return it */
  if (isAbsolute(identifier)) return identifier;

  /** get parts of identifier */
  const prefix = identifier.split(":")[0] || "";
  let id = identifier.split(":")[1] || "";

  /** oMIM:1234.123 -> OMIM:1234#123 */
  if (prefix === "OMIM") id = id.replace(".", "#");

  /** get link template from map */
  const url = (map[prefix.toLowerCase()] || {})[prefix] || "";

  /** make id replacements */
  return url.replace("[ID]", id);
};

/**
 * hard coded map of external reference urls based on identifier prefix. keep
 * sorted. https://r37r0m0d3l.github.io/json_sort/
 */
const map: { [key: string]: { [key: string]: string } } = {
  animalqtldb: {
    AQTLPub:
      "https://www.animalgenome.org/cgi-bin/QTLdb/BT/qabstract?PUBMED_ID=[ID]",
    AQTLTrait: "http://identifiers.org/animalqtltrait/[ID]",
    catfishQTL:
      "https://www.animalgenome.org/cgi-bin/QTLdb/IP/qdetails?QTL_ID=[ID]",
    cattleQTL:
      "https://www.animalgenome.org/cgi-bin/QTLdb/BT/qdetails?QTL_ID=[ID]",
    chickenQTL:
      "https://www.animalgenome.org/cgi-bin/QTLdb/GG/qdetails?QTL_ID=[ID]",
    horseQTL:
      "https://www.animalgenome.org/cgi-bin/QTLdb/EC/qdetails?QTL_ID=[ID]",
    pigQTL:
      "https://www.animalgenome.org/cgi-bin/QTLdb/SS/qdetails?QTL_ID=[ID]",
    rainbow_troutQTL:
      "https://www.animalgenome.org/cgi-bin/QTLdb/OM/qdetails?QTL_ID=[ID]",
    sheepQTL:
      "https://www.animalgenome.org/cgi-bin/QTLdb/OA/qdetails?QTL_ID=[ID]",
  },
  apb: {
    APB: "http://pb.apf.edu.au/phenbank/strain.html?id=[ID]",
  },
  apo: {
    APO: "http://purl.obolibrary.org/obo/APO_[ID]",
  },
  aspgd: {
    AspGD: "http://www.aspergillusgenome.org/cgi-bin/locus.pl?dbid=[ID]",
  },
  aspgd_ref: {
    AspGD_REF:
      "http://www.aspergillusgenome.org/cgi-bin/reference/reference.pl?dbid=[ID]",
  },
  bfo: {
    BFO: "http://purl.obolibrary.org/obo/BFO_[ID]",
  },
  biogrid: {
    BIOGRID: "http://thebiogrid.org/[ID]",
  },
  bt: {
    BT: "http://c.biothings.io/#[ID]",
  },
  ccds: {
    CCDS: "http://www.ncbi.nlm.nih.gov/CCDS/CcdsBrowse.cgi?REQUEST=CCDS&DATA=[ID]",
  },
  cgnc: {
    CGNC: "http://birdgenenames.org/cgnc/GeneReport?id=[ID]",
  },
  chebi: {
    CHEBI: "http://purl.obolibrary.org/obo/CHEBI_[ID]",
  },
  chr: {
    CHR: "http://purl.obolibrary.org/obo/CHR_[ID]",
  },
  cid: {
    CID: "http://pubchem.ncbi.nlm.nih.gov/compound/[ID]",
  },
  cito: {
    cito: "http://purl.org/spar/cito/[ID]",
  },
  cl: {
    CL: "http://purl.obolibrary.org/obo/CL_[ID]",
  },
  clinvar: {
    ClinVar: "http://www.ncbi.nlm.nih.gov/clinvar/[ID]",
    ClinVarSubmitters: "http://www.ncbi.nlm.nih.gov/clinvar/submitters/[ID]",
    ClinVarVariant: "http://www.ncbi.nlm.nih.gov/clinvar/variation/[ID]",
  },
  clo: {
    CLO: "http://purl.obolibrary.org/obo/CLO_[ID]",
  },
  cmmr: {
    CMMR: "http://www.cmmr.ca/order.php?t=m&id=[ID]",
  },
  cmo: {
    CMO: "http://purl.obolibrary.org/obo/CMO_[ID]",
  },
  coriell: {
    Coriell:
      "https://catalog.coriell.org/0/Sections/Search/Sample_Detail.aspx?Ref=[ID]",
    CoriellCollection: "https://catalog.coriell.org/1/[ID]",
    CoriellFamily:
      "https://catalog.coriell.org/0/Sections/BrowseCatalog/FamilyTypeSubDetail.aspx?fam=[ID]",
    CoriellIndividual: "https://catalog.coriell.org/Search?q=[ID]",
  },
  coriellcollection: {
    CoriellCollection: "https://catalog.coriell.org/1/[ID]",
  },
  cosmic: {
    COSMIC: "http://cancer.sanger.ac.uk/cosmic/mutation/overview?id=[ID]",
  },
  dbsnp: {
    dbSNP: "http://www.ncbi.nlm.nih.gov/projects/SNP/snp_ref.cgi?rs=[ID]",
  },
  dbsnpindividual: {
    dbSNPIndividual: "http://www.ncbi.nlm.nih.gov/SNP/snp_ind.cgi?ind_id=[ID]",
  },
  dbvar: {
    dbVar: "http://www.ncbi.nlm.nih.gov/dbvar/[ID]",
  },
  dc_cl: {
    DC_CL: "http://purl.obolibrary.org/obo/DC_CL[ID]",
  },
  decipher: {
    DECIPHER: "https://decipher.sanger.ac.uk/syndrome/[ID]",
  },
  dictybase: {
    dictyBase: "http://dictybase.org/gene/[ID]",
  },
  doi: {
    DOI: "http://dx.doi.org/[ID]",
  },
  doid: {
    DOID: "http://purl.obolibrary.org/obo/DOID_[ID]",
  },
  drugbank: {
    DrugBank: "http://www.drugbank.ca/drugs/[ID]",
  },
  ec: {
    EC: "https://www.enzyme-database.org/query.php?ec=[ID]",
  },
  eco: {
    ECO: "http://purl.obolibrary.org/obo/ECO_[ID]",
  },
  ecogene: {
    EcoGene: "http://ecogene.org/gene/[ID]",
  },
  "edam-data": {
    "EDAM-DATA": "http://edamontology.org/data_[ID]",
  },
  efo: {
    EFO: "http://www.ebi.ac.uk/efo/EFO_[ID]",
  },
  emapa: {
    EMAPA: "http://purl.obolibrary.org/obo/EMAPA_[ID]",
  },
  emma: {
    EMMA: "https://www.infrafrontier.eu/search?keyword=EM:[ID]",
  },
  ensembl: {
    ENSEMBL: "http://ensembl.org/id/[ID]",
    EnsemblGenome: "http://www.ensemblgenomes.org/id/[ID]",
  },
  envo: {
    ENVO: "http://purl.obolibrary.org/obo/ENVO_[ID]",
  },
  eom: {
    EOM: "https://elementsofmorphology.nih.gov/index.cgi?tid=[ID]",
  },
  ero: {
    ERO: "http://purl.obolibrary.org/obo/ERO_[ID]",
  },
  faldo: {
    faldo: "http://biohackathon.org/resource/faldo#[ID]",
  },
  fbbt: {
    FBbt: "http://purl.obolibrary.org/obo/FBbt_[ID]",
  },
  fbcv: {
    FBcv: "http://purl.obolibrary.org/obo/FBcv_[ID]",
  },
  fbdv: {
    FBdv: "http://purl.obolibrary.org/obo/FBdv_[ID]",
  },
  fdadrug: {
    FDADrug: "http://www.fda.gov/Drugs/InformationOnDrugs/[ID]",
  },
  flybase: {
    FlyBase: "http://flybase.org/reports/[ID]",
  },
  genatlas: {
    Genatlas: "http://genatlas.medecine.univ-paris5.fr/fiche.php?symbol=[ID]",
  },
  genbank: {
    GenBank: "http://www.ncbi.nlm.nih.gov/nuccore/[ID]",
  },
  genereviews: {
    GeneReviews: "http://www.ncbi.nlm.nih.gov/books/[ID]",
  },
  geno: {
    GENO: "http://purl.obolibrary.org/obo/GENO_[ID]",
  },
  ginas: {
    GINAS: "http://tripod.nih.gov/ginas/app/substance#[ID]",
  },
  go: {
    GO: "http://amigo.geneontology.org/amigo/term/GO:[ID]",
    GO_REF: "http://www.geneontology.org/cgi-bin/references.cgi#GO_REF:[ID]",
    PAINT_REF:
      "http://www.geneontology.org/gene-associations/submission/paint/[ID]",
  },
  gwascatalog: {
    dbSNP: "https://www.ebi.ac.uk/gwas/variants/[ID]",
    ENSEMBL: "https://www.ebi.ac.uk/gwas/genes/[ID]",
    GWAS: "https://www.ebi.ac.uk/gwas/variants/[ID]",
  },
  hgmd: {
    HGMD: "http://www.hgmd.cf.ac.uk/ac/gene.php?gene=[ID]",
  },
  hgnc: {
    HGNC: "https://www.genenames.org/data/gene-symbol-report/#!/hgnc_id/HGNC:[ID]",
  },
  hmdb: {
    HMDB: "http://www.hmdb.ca/metabolites/[ID]",
  },
  homologene: {
    HOMOLOGENE: "http://www.ncbi.nlm.nih.gov/homologene/[ID]",
  },
  hp: {
    HP: "http://purl.obolibrary.org/obo/HP_[ID]",
  },
  hpoa: {
    HP: "https://hpo.jax.org/app/browse/term/HP:[ID]",
    OMIM: "http://omim.org/entry/[ID]",
    OMIMPS: "http://www.omim.org/phenotypicSeries/[ID]",
    ORPHA: "https://www.orpha.net/consor/cgi-bin/OC_Exp.php?Lng=EN&Expert=[ID]",
  },
  hprd: {
    HPRD: "http://www.hprd.org/protein/[ID]",
  },
  iao: {
    IAO: "http://purl.obolibrary.org/obo/IAO_[ID]",
  },
  impc: {
    IMPC: "http://www.mousephenotype.org/data/genes/[ID]",
    "IMPRESS-parameter":
      "https://www.mousephenotype.org/impress/parameterontologies/[ID]",
    "IMPRESS-procedure":
      "https://www.mousephenotype.org/impress/procedures/[ID]",
    "IMPRESS-protocol": "https://www.mousephenotype.org/impress/protocol/[ID]",
    MGI: "https://www.mousephenotype.org/data/genes/MGI:[ID]",
    MP: "https://www.mousephenotype.org/data/phenotypes/MP:[ID]",
  },
  isbn: {
    ISBN: "https://monarchinitiative.org/ISBN_[ID]",
  },
  "isbn-10": {
    "ISBN-10": "https://monarchinitiative.org/ISBN10_[ID]",
  },
  "isbn-13": {
    "ISBN-13": "https://monarchinitiative.org/ISBN13_[ID]",
  },
  iuphar: {
    IUPHAR:
      "http://www.guidetopharmacology.org/GRAC/ObjectDisplayForward?objectId=[ID]",
  },
  jax: {
    JAX: "http://jaxmice.jax.org/strain/[ID]",
  },
  kegg: {
    "KEGG-ds": "http://purl.obolibrary.org/KEGG-ds_[ID]",
    "KEGG-hsa": "http://www.kegg.jp/dbget-bin/www_bget?hsa:[ID]",
    "KEGG-img": "http://www.genome.jp/kegg/pathway/map/map[ID]",
    "KEGG-ko": "http://www.kegg.jp/dbget-bin/www_bget?ko:[ID]",
    "KEGG-path": "http://www.kegg.jp/dbget-bin/www_bget?path:[ID]",
  },
  lpt: {
    LPT: "http://purl.obolibrary.org/obo/LPT_[ID]",
  },
  ma: {
    MA: "http://purl.obolibrary.org/obo/MA_[ID]",
  },
  meddra: {
    MEDDRA: "http://purl.bioontology.org/ontology/MEDDRA/[ID]",
  },
  medgen: {
    MedGen: "http://www.ncbi.nlm.nih.gov/medgen/[ID]",
  },
  mgi: {
    J: "http://www.informatics.jax.org/reference/J:[ID]",
    MGI: "http://www.informatics.jax.org/accession/MGI:[ID]",
    MP: "http://www.informatics.jax.org/vocab/mp_ontology/MP:[ID]",
  },
  mirbase: {
    miRBase: "http://www.mirbase.org/cgi-bin/mirna_entry.pl?acc=[ID]",
  },
  mmrrc: {
    MMRRC: "https://www.mmrrc.org/catalog/sds.php?mmrrc_id=[ID]",
  },
  monarcharchive: {
    MonarchArchive: "https://archive.monarchinitiative.org/[ID]",
  },
  mpath: {
    MPATH: "http://purl.obolibrary.org/obo/MPATH_[ID]",
  },
  mpd: {
    MPD: "https://phenome.jax.org/[ID]",
    "MPD-assay":
      "https://phenome.jax.org/db/qp?rtn=views/catlines&keymeas=[ID]",
    "MPD-strain":
      "http://phenome.jax.org/db/q?rtn=strains/details&strainid=[ID]",
  },
  mugen: {
    MUGEN:
      "http://bioit.fleming.gr/mugen/Controller?workflow=ViewModel&expand_all=true&name_begins=model.block&eid=[ID]",
  },
  nbo: {
    NBO: "http://purl.obolibrary.org/obo/NBO_[ID]",
  },
  ncbiassembly: {
    NCBIAssembly: "https://www.ncbi.nlm.nih.gov/assembly?term=[ID]",
  },
  ncbigene: {
    NCBIGene: "https://www.ncbi.nlm.nih.gov/gene/[ID]",
  },
  ncbigenome: {
    NCBIGenome: "https://www.ncbi.nlm.nih.gov/genome/[ID]",
  },
  ncbiprotein: {
    NCBIProtein: "http://www.ncbi.nlm.nih.gov/protein/[ID]",
  },
  ncbitaxon: {
    // NCBITaxon: "http://purl.obolibrary.org/obo/NCBITaxon_[ID]",
    NCBITaxon:
      "https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=info&id=[ID]",
  },
  ncimr: {
    NCIMR: "https://mouse.ncifcrf.gov/available_details.asp?ID=[ID]",
  },
  ncit: {
    NCIT: "http://purl.obolibrary.org/obo/NCIT_[ID]",
  },
  oae: {
    OAE: "http://purl.obolibrary.org/obo/OAE_[ID]",
  },
  oba: {
    OBA: "http://purl.obolibrary.org/obo/OBA_[ID]",
  },
  obo: {
    OBO: "http://purl.obolibrary.org/obo/[ID]",
  },
  omia: {
    OMIA: "https://omia.org/OMIA[ID]",
    "OMIA-breed": "https://monarchinitiative.org/model/OMIA-breed:[ID]",
  },
  omim: {
    OMIM: "http://omim.org/entry/[ID]",
    OMIMPS: "http://www.omim.org/phenotypicSeries/[ID]",
  },
  orphanet: {
    ORPHA: "https://www.orpha.net/consor/cgi-bin/OC_Exp.php?Lng=EN&Expert=[ID]",
    Orphanet:
      "https://www.orpha.net/consor/cgi-bin/OC_Exp.php?Lng=EN&Expert=[ID]",
  },
  panther: {
    PANTHER: "http://www.pantherdb.org/panther/family.do?clsAccession=[ID]",
  },
  pato: {
    PATO: "http://purl.obolibrary.org/obo/PATO_[ID]",
  },
  pco: {
    PCO: "http://purl.obolibrary.org/obo/PCO_[ID]",
  },
  pdb: {
    PDB: "http://www.ebi.ac.uk/pdbsum/[ID]",
  },
  pmcid: {
    PMCID: "http://www.ncbi.nlm.nih.gov/pmc/[ID]",
  },
  pmid: {
    PMID: "http://www.ncbi.nlm.nih.gov/pubmed/[ID]",
  },
  pombase: {
    PomBase: "https://www.pombase.org/spombe/result/[ID]",
  },
  pr: {
    PR: "http://purl.obolibrary.org/obo/PR_[ID]",
  },
  pw: {
    PW: "http://purl.obolibrary.org/obo/PW_[ID]",
  },
  rbrc: {
    RBRC: "http://www2.brc.riken.jp/lab/animal/detail.php?brc_no=RBRC[ID]",
  },
  react: {
    REACT: "http://www.reactome.org/PathwayBrowser/#/[ID]",
  },
  refseq: {
    RefSeq: "http://www.ncbi.nlm.nih.gov/refseq/?term=[ID]",
  },
  rgd: {
    RGD: "http://rgd.mcw.edu/rgdweb/report/gene/main.html?id=[ID]",
    RGDRef: "http://rgd.mcw.edu/rgdweb/report/reference/main.html?id=[ID]",
  },
  ro: {
    RO: "http://purl.obolibrary.org/obo/RO_[ID]",
  },
  rxcui: {
    RXCUI: "http://purl.bioontology.org/ontology/RXNORM/[ID]",
  },
  sepio: {
    SEPIO: "http://purl.obolibrary.org/obo/SEPIO_[ID]",
  },
  sgd: {
    SGD: "https://www.yeastgenome.org/locus/[ID]",
    SGD_REF: "https://www.yeastgenome.org/reference/[ID]",
  },
  sio: {
    SIO: "http://semanticscience.org/resource/SIO_[ID]",
  },
  smpdb: {
    SMPDB: "http://smpdb.ca/view/[ID]",
  },
  snomed: {
    SNOMED: "http://purl.obolibrary.org/obo/SNOMED_[ID]",
  },
  so: {
    SO: "http://purl.obolibrary.org/obo/SO_[ID]",
  },
  stato: {
    STATO: "http://purl.obolibrary.org/obo/STATO_[ID]",
  },
  string: {
    home: "https://string-db.org",
  },
  swissprot: {
    SwissProt: "http://identifiers.org/SwissProt:[ID]",
  },
  tair: {
    TAIR: "https://www.arabidopsis.org/servlets/TairObject?type=locus&id=[ID]",
  },
  trembl: {
    TrEMBL: "http://purl.uniprot.org/uniprot/[ID]",
  },
  uberon: {
    UBERON: "http://purl.obolibrary.org/obo/UBERON_[ID]",
  },
  ucscbands: {
    UCSC: "ftp://hgdownload.cse.ucsc.edu/goldenPath/[ID]",
    UCSCBuild: "http://genome.ucsc.edu/cgi-bin/hgGateway?db=[ID]",
  },
  umls: {
    UMLS: "http://linkedlifedata.com/resource/umls/id/[ID]",
  },
  unii: {
    UNII: "http://fdasis.nlm.nih.gov/srs/unii/[ID]",
  },
  uniprotkb: {
    UniProtKB: "http://identifiers.org/uniprot/[ID]",
  },
  uo: {
    UO: "http://purl.obolibrary.org/obo/UO_[ID]",
  },
  vfb: {
    vfb: "http://virtualflybrain.org/reports/[ID]",
  },
  vgnc: {
    VGNC: "https://vertebrate.genenames.org/data/gene-symbol-report/#!/vgnc_id/[ID]",
  },
  vivo: {
    VIVO: "http://vivoweb.org/ontology/core#[ID]",
  },
  vt: {
    VT: "http://purl.obolibrary.org/obo/VT_[ID]",
  },
  wbbt: {
    WBbt: "http://purl.obolibrary.org/obo/WBbt_[ID]",
  },
  wbphenotype: {
    WBPhenotype: "http://purl.obolibrary.org/obo/WBPhenotype_[ID]",
  },
  wikidata: {
    WD_Entity: "https://www.wikidata.org/wiki/[ID]",
    WD_Prop: "https://www.wikidata.org/wiki/Property:[ID]",
  },
  wormbase: {
    WormBase: "https://www.wormbase.org/get?name=[ID]",
  },
  xao: {
    XAO: "http://purl.obolibrary.org/obo/XAO_[ID]",
  },
  xco: {
    XCO: "http://purl.obolibrary.org/obo/XCO_[ID]",
  },
  xenbase: {
    Xenbase:
      "http://www.xenbase.org/gene/showgene.do?method=display&geneId=[ID]",
  },
  zfa: {
    ZFA: "http://purl.obolibrary.org/obo/ZFA_[ID]",
  },
  zfin: {
    ZFIN: "http://zfin.org/[ID]",
  },
  zfs: {
    ZFS: "http://purl.obolibrary.org/obo/ZFS_[ID]",
  },
  zp: {
    ZP: "http://purl.obolibrary.org/obo/ZP_[ID]",
  },
};
