"""Response models for the association summary endpoint (/entity/{id}/{section}/summary).

A summary is the facet-only view of an entity's association section: totals over the
whole section, plus one bucket per value of a `group_by` field (e.g. one per drug on a
disease page), each carrying distinct counts, min/max values, a representative value
and term facets of its own. It never returns association rows; the table endpoint,
filtered to a group, does that.
"""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SummaryFacetValue(BaseModel):
    value: str
    count: int
    label: Optional[str] = Field(
        default=None, description="The value's most common label, when the facet has a label field (facet_labels)"
    )


class SummaryStat(BaseModel):
    min: Optional[str] = None
    max: Optional[str] = None


class AssociationSummaryGroup(BaseModel):
    value: str = Field(description="The group_by field's value for this bucket")
    count: int = Field(description="Number of association rows in the bucket")
    unique: Dict[str, int] = Field(default_factory=dict, description="Distinct values per unique_fields entry")
    stats: Dict[str, SummaryStat] = Field(default_factory=dict, description="Min/max per stat_fields entry")
    fields: Dict[str, Optional[str]] = Field(
        default_factory=dict, description="Most common value per label_fields entry (e.g. the group's label)"
    )
    facets: Dict[str, List[SummaryFacetValue]] = Field(
        default_factory=dict, description="Term facets per facet_fields entry"
    )


class AssociationSummary(BaseModel):
    total: int = Field(description="Number of association rows in the section")
    group_by: str
    group_total: int = Field(description="Number of distinct group_by values (groups) in the section")
    offset: int = 0
    limit: int = 20
    unique: Dict[str, int] = Field(default_factory=dict, description="Distinct values per unique_fields, section-wide")
    facets: Dict[str, List[SummaryFacetValue]] = Field(
        default_factory=dict, description="Term facets per facet_fields entry, section-wide"
    )
    groups: List[AssociationSummaryGroup] = Field(default_factory=list)
