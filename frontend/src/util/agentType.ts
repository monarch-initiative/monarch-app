/** Centralized metadata for Biolink AgentTypeEnum values. */

type AgentTypeMeta = { icon: string; label: string; description: string };

const AGENT_TYPE_META: Record<string, AgentTypeMeta> = {
  manual_agent: {
    icon: "user",
    label: "Manual Agent",
    description: "A human agent responsible for generating the statement",
  },
  automated_agent: {
    icon: "robot",
    label: "Automated Agent",
    description: "An automated software program or tool",
  },
  data_analysis_pipeline: {
    icon: "bars-progress",
    label: "Data Analysis Pipeline",
    description: "Executes workflows and reports direct statistical results",
  },
  computational_model: {
    icon: "cogs",
    label: "Computational Model",
    description: "Generates predictions using rules or learned patterns",
  },
  text_mining_agent: {
    icon: "file-lines",
    label: "Text Mining Agent",
    description: "Uses NLP to recognize concepts and relationships in text",
  },
  image_processing_agent: {
    icon: "image",
    label: "Image Processing Agent",
    description: "Processes images to produce knowledge statements",
  },
  manual_validation_of_automated_agent: {
    icon: "user-gear",
    label: "Manual Validation of Automated Agent",
    description: "Human-reviewed automated output",
  },
  not_provided: {
    icon: "circle-question",
    label: "Not Provided",
    description: "Agent type not available",
  },
};

const FALLBACK: AgentTypeMeta = {
  icon: "circle-question",
  label: "Unknown",
  description: "Unrecognized agent type",
};

/** Get icon, label, and description for an agent_type value. */
export function getAgentTypeMeta(agentType: string): AgentTypeMeta {
  return AGENT_TYPE_META[agentType] ?? FALLBACK;
}

/** Format an agent_type value as a human-readable label. */
export function formatAgentType(agentType: string): string {
  return getAgentTypeMeta(agentType).label;
}
