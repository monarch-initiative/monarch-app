import type { IconDefinition } from "@fortawesome/fontawesome-svg-core";
import { library } from "@fortawesome/fontawesome-svg-core";
import * as fab from "@fortawesome/free-brands-svg-icons";
import * as fas from "@fortawesome/free-solid-svg-icons";

/** create collection/"palette" of useable icons */

const icons: IconDefinition[] = [
  fab.faGithub,
  fab.faMastodon,
  fab.faMedium,
  fab.faTwitter,
  fas.faAngleDoubleLeft,
  fas.faAngleDoubleRight,
  fas.faAngleDown,
  fas.faAngleLeft,
  fas.faAngleRight,
  fas.faAngleUp,
  fas.faArrowDown,
  fas.faArrowDownLong,
  fas.faArrowLeft,
  fas.faArrowLeftLong,
  fas.faArrowRight,
  fas.faArrowRightLong,
  fas.faArrowsLeftRight,
  fas.faArrowUp,
  fas.faArrowUpLong,
  fas.faAsterisk,
  fas.faBalanceScale,
  fas.faBars,
  fas.faBarsProgress,
  fas.faBlog,
  fas.faBook,
  fas.faCalendarAlt,
  fas.faChartBar,
  fas.faCheck,
  fas.faCheckCircle,
  fas.faClipboard,
  fas.faClipboardList,
  fas.faClockRotateLeft,
  fas.faCode,
  fas.faCogs,
  fas.faComment,
  fas.faComments,
  fas.faCopy,
  fas.faDatabase,
  fas.faDownload,
  fas.faEquals,
  fas.faExclamationCircle,
  fas.faExternalLinkAlt,
  fas.faEye,
  fas.faFeatherAlt,
  fas.faFileLines,
  fas.faFilter,
  fas.faFlask,
  fas.faFloppyDisk,
  fas.faHandsHelping,
  fas.faHashtag,
  fas.faHistory,
  fas.faHome,
  fas.faInfoCircle,
  fas.faLightbulb,
  fas.faLink,
  fas.faLocationDot,
  fas.faMaximize,
  fas.faMinimize,
  fas.faNewspaper,
  fas.faNotesMedical,
  fas.faPaperPlane,
  fas.faPauseCircle,
  fas.faPersonRunning,
  fas.faPuzzlePiece,
  fas.faQuestionCircle,
  fas.faSearch,
  fas.faSignature,
  fas.faSitemap,
  fas.faSquare,
  fas.faSquareCheck,
  fas.faSubscript,
  fas.faTable,
  fas.faTimes,
  fas.faTimesCircle,
  fas.faToolbox,
  fas.faTools,
  fas.faUpload,
  fas.faUsers,
  fas.faXmark,
];

library.add(...icons);