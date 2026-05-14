const baseMessages = {
  brandTag: "Student job-search execution system",
  navHome: "Home",
  navDashboard: "Workspace",
  navOperations: "Signals",
  navOpportunities: "Opportunities",
  navStudio: "Resume Quest",
  languageLabel: "Language",
  heroEyebrow: "AI job-search agent for students",
  heroTitle: "Help students turn messy experience into real applications.",
  heroBody:
    "Resume Copilot starts with the resume because that is where student job search breaks first: unclear evidence, weak role fit, and no execution loop after each application.",
  heroPrimary: "Open Resume Lab",
  heroSecondary: "Start Resume Quest",
  heroPoint1:
    "Positioning: for students who have raw potential but cannot package it into hiring evidence yet",
  heroPoint2:
    "Product wedge: resume diagnosis, JD alignment, generation, opportunity scoring, and feedback learning",
  heroPoint3:
    "North star: help one real candidate move from rough materials to interviews, then scale the loop",
  positioningAudienceLabel: "For",
  positioningAudience: "Students entering the job market",
  positioningWedgeLabel: "Wedge",
  positioningWedge: "Resume first, execution next",
  positioningOutcomeLabel: "Outcome",
  positioningOutcome: "From rough material to tracked applications",
  previewLabel: "Workbench outputs",
  preview1: "Resume diagnosis report",
  preview2: "JD alignment analysis",
  preview3: "Rewrite candidates",
  preview4: "Next action queue",
  studioEyebrow: "Resume Lab",
  studioTitle: "The resume is the first battlefield.",
  studioBody:
    "Feed a target role, a JD, and rough student material. The workbench turns scattered experience into diagnosis, keyword gaps, rewrite directions, and a concrete execution queue.",
  dashboardEyebrow: "Workspace",
  dashboardTitle: "One student, one job-search operating console.",
  dashboardBody:
    "The workspace connects profile, target roles, resume versions, opportunities, applications, interview prep, and feedback memory so the product is not just a resume generator.",
  operationsEyebrow: "Signals",
  operationsTitle: "Turn campus signals into hiring evidence.",
  operationsBody:
    "Keep the input surface small: raw materials, target roles, resume versions, applications, and feedback. The product should feel like a coach with memory, not a form warehouse.",
  opportunitiesEyebrow: "Opportunities",
  opportunitiesTitle: "Not every job deserves the same energy.",
  opportunitiesBody:
    "Opportunity Agent scores fit, shows risk, suggests the best resume version, and converts promising roles into tracked applications.",
  workspaceKicker: "Candidate",
  modulesKicker: "Modules",
  targetsKicker: "Targets",
  resumeVersionsKicker: "Resume versions",
  profileFormKicker: "Profile",
  targetFormKicker: "Targeting",
  resumeVersionFormKicker: "Resume ops",
  applicationFormKicker: "Applications",
  opportunityFormKicker: "Import opportunity",
  opportunityListKicker: "Recommended opportunities",
  fieldFullName: "Full name",
  fieldTargetTitle: "Primary target role",
  fieldTargetMarkets: "Target markets",
  fieldStrengths: "Top strengths",
  fieldTargetRole: "Role title",
  fieldTargetMarket: "Market",
  fieldSeniority: "Seniority",
  fieldPriorities: "Priorities",
  fieldResumeLabel: "Version label",
  fieldResumeStatus: "Status",
  fieldResumeFocus: "Focus",
  fieldResumeMarket: "Market",
  fieldCompany: "Company",
  fieldApplicationRole: "Role",
  fieldApplicationStage: "Stage",
  fieldNextStep: "Next step",
  fieldOpportunityCompany: "Company",
  fieldOpportunityTitle: "Role title",
  fieldOpportunityMarket: "Market",
  fieldOpportunityLocation: "Location",
  fieldOpportunitySource: "Source",
  fieldOpportunityDescription: "Job description",
  fieldMarket: "Target market",
  fieldTone: "Voice preference",
  fieldRole: "Target role",
  fieldResume: "Resume snapshot",
  fieldJd: "Job description excerpt",
  saveProfile: "Save profile",
  addTarget: "Add target",
  addResumeVersion: "Add resume version",
  trackApplication: "Track application",
  scoreOpportunity: "Score opportunity",
  applySuggested: "Add to applications",
  runPreview: "Run workbench",
  commandDeck: "Command Deck",
  workbenchInput: "Quest Builder",
  liveStatus: "live",
  saveWorkbenchVersion: "Save as version",
  generateWorkbenchDocument: "Generate resume file",
  formatLatex: "LaTeX .tex",
  formatDocx: "Word .docx",
  loadSample: "Load sample",
  commandLog: "Command Log",
  signalMatrix: "Resume Health",
  diagnosis: "Diagnosis",
  keywordStack: "Keyword Stack",
  matchedKeywords: "Matched",
  missingKeywords: "Missing",
  focusAreas: "Focus Areas",
  rewriteCandidates: "Rewrite Candidates",
  nextActions: "Next Actions",
  generationPlan: "Generation Plan",
  generationResult: "Generation Result",
  rawIntake: "Raw intake",
  rawIntakeCopy: "Turn messy campus material into a first structured master draft.",
  education: "Education",
  major: "Major",
  graduationCycle: "Graduation cycle",
  messyRawMaterials: "Messy raw materials",
  createFirstDraft: "Create first draft",
  feedbackLoop: "Feedback loop",
  result: "Result",
  notes: "Notes",
  recordFeedback: "Record feedback",
  batchOpportunities: "Batch opportunities",
  runBatchRanking: "Run batch ranking",
  metricJdMatch: "JD Match",
  metricEvidence: "Evidence",
  metricReadability: "Readability",
  metricAtsSafety: "ATS Safety",
  before: "Before",
  after: "After",
  noGeneratedFile: "No generated file yet. Save a version first, or generate a resume file from the current workbench state.",
  generatedStatus: "Status: generated and attached to the latest resume version.",
  downloadFile: "Download file",
  generatedFileReady: "Your resume file is ready",
  outputPath: "Output path",
  suggestion: "Suggestion",
  failedStatus: "Status: failed",
  errorLabel: "Error",
  emptyOpportunitiesTitle: "No opportunities ranked yet",
  emptyOpportunitiesBody: "Import a role or run a batch ranking pass to start building your opportunity queue.",
  emptyBoardTitle: "Your opportunity board is empty",
  emptyBoardBody: "Strong opportunities will appear here once you import and score roles.",
  resumeLabel: "Resume",
  missingSignalLabel: "missing signals",
  riskFlagLabel: "risk flags",
  savingVersion: "Saving version...",
  generatingFile: "Generating file...",
  orbitCore: "Execution loop online",
  orbitResume: "diagnose / rewrite / export",
  orbitMatch: "keywords / evidence / gaps",
  orbitDeploy: "version / docx / apply-ready",
  orbitLoop: "results / interview / retarget",
  systemModeLabel: "System mode",
  primaryPathLabel: "Primary path",
  primaryPathValue: "resume -> JD -> application",
  systemStatusLabel: "Status",
  systemStatusValue: "live / editable",
  marketUs: "United States",
  marketUk: "United Kingdom",
  marketEu: "European Union",
  marketApac: "APAC",
  marketRemote: "Remote-first",
  tonePrecise: "Precise",
  toneConfident: "Confident",
  toneTechnical: "Technical",
  fieldExactRoleNote: "Use the exact role title you want this version to win.",
  fieldResumeNote: "Paste raw bullets, rough notes, or half-finished resume content. The system is designed to work from imperfect input.",
  fieldJdNote: "Include the lines that reveal hiring signals, stack requirements, and evaluation criteria.",
  rawIntakeNote: "Dump competitions, clubs, project notes, half-written bullets, or anything worth packaging.",
  placeholderEducation: "Tsinghua University",
  placeholderMajor: "Computer Science",
  placeholderGraduation: "2026",
  placeholderFullName: "Jane Candidate",
  placeholderTargetTitle: "Senior Backend Engineer",
  placeholderTargetMarkets: "US, UK, Remote",
  placeholderStrengths: "Distributed systems, Python, mentorship",
  placeholderTargetRole: "Platform Engineer",
  placeholderTargetMarket: "Remote",
  placeholderSeniority: "Senior IC",
  placeholderPriorities: "Scale, reliability, async collaboration",
  placeholderResumeLabel: "US backend tailored v2",
  placeholderResumeStatus: "Ready",
  placeholderResumeFocus: "Python, distributed systems, mentoring",
  placeholderResumeMarket: "US",
  placeholderApplicationCompany: "Atlas Cloud",
  placeholderApplicationRole: "Senior Backend Engineer",
  placeholderApplicationStage: "Tailoring",
  placeholderApplicationNextStep: "Finalize resume and submit",
  placeholderFeedbackCompany: "Atlas Cloud",
  placeholderFeedbackRole: "Senior Backend Engineer",
  placeholderFeedbackResult: "Interview / Rejected / Offer",
  placeholderFeedbackNotes: "Rejected due to weaker system design depth.",
  placeholderOpportunityCompany: "Signal Stack",
  placeholderOpportunityTitle: "Senior Backend Engineer",
  placeholderOpportunityMarket: "US",
  placeholderOpportunityLocation: "Remote / US",
  placeholderOpportunitySource: "LinkedIn import",
  placeholderBatchOpportunity: "[{\"company\":\"Orbit Works\",\"title\":\"Platform Engineer\",\"market\":\"US\",\"location\":\"Remote / US\",\"description\":\"Python platform role with reliability and ownership.\"}]",
  opportunityListCopy: "Score what deserves attention, then convert only the strongest matches into action.",
  emptyToken: "none",
  commandWaiting: "Answer the levels on the left. AI suggestions will appear here after you run the workbench.",
  unavailable: "unavailable",
  unknownGenerationError: "unknown generation error",
  resumeTbd: "TBD",
  roleLabel: "Role",
  sourceLabel: "Source",
  fileLabel: "File",
  noNextStep: "No next step captured yet.",
  zhSampleOpportunityDescription: "Looking for a backend engineer with Python, distributed systems, reliability, and stakeholder communication experience.",
  zhSampleRawIntake: "Competition: ACM contest finalist.\nCourse project: built a campus mini app with Python backend.\nStudent club: organized a recruiting event for 300 participants.",
};

const zhMessages = {
  brandTag: "\u6c42\u804c\u6267\u884c\u4e2d\u5fc3",
  navHome: "\u9996\u9875",
  navDashboard: "\u5de5\u4f5c\u53f0",
  navOperations: "\u4fe1\u53f7\u5f55\u5165",
  navOpportunities: "\u5c97\u4f4d\u673a\u4f1a",
  navStudio: "\u7b80\u5386\u95ef\u5173",
  languageLabel: "\u8bed\u8a00",
  heroEyebrow: "\u9762\u5411\u5927\u5b66\u751f\u7684 AI \u6c42\u804c\u7cfb\u7edf",
  heroTitle: "\u5e2e\u5927\u5b66\u751f\u628a\u6df7\u4e71\u7ecf\u5386\u53d8\u6210\u771f\u6b63\u7684\u6295\u9012\u529b",
  heroBody:
    "\u5148\u4ece\u7b80\u5386\u5207\u5165\uff0c\u56e0\u4e3a\u5927\u5b66\u751f\u6c42\u804c\u6700\u5148\u5361\u4f4f\u7684\u5f80\u5f80\u4e0d\u662f\u6ca1\u80fd\u529b\uff0c\u800c\u662f\u4e0d\u4f1a\u628a\u7ecf\u5386\u5305\u88c5\u6210\u5c97\u4f4d\u770b\u5f97\u61c2\u7684\u8bc1\u636e\u3002",
  heroPrimary: "\u8fdb\u5165\u7b80\u5386\u5b9e\u9a8c\u5ba4",
  heroSecondary: "\u8fdb\u5165\u7b80\u5386\u95ef\u5173",
  heroPoint1: "\u5b9a\u4f4d\uff1a\u9762\u5411\u6709\u6f5c\u529b\u3001\u4f46\u7ecf\u5386\u5305\u88c5\u80fd\u529b\u4e0d\u8db3\u7684\u5927\u5b66\u751f",
  heroPoint2: "\u5207\u53e3\uff1a\u4ece\u7b80\u5386\u8bca\u65ad\u3001JD \u5bf9\u9f50\u3001\u6587\u4ef6\u751f\u6210\u8d70\u5230\u5c97\u4f4d\u6392\u5e8f\u548c\u53cd\u9988\u5b66\u4e60",
  heroPoint3: "\u5317\u6781\u661f\uff1a\u5148\u5e2e\u4e00\u4e2a\u771f\u5b9e\u5019\u9009\u4eba\u627e\u5230\u5de5\u4f5c\uff0c\u518d\u628a\u8fd9\u5957\u56de\u8def\u89c4\u6a21\u5316",
  positioningAudienceLabel: "\u670d\u52a1\u5bf9\u8c61",
  positioningAudience: "\u8fdb\u5165\u6c42\u804c\u6218\u573a\u7684\u5927\u5b66\u751f",
  positioningWedgeLabel: "\u4ea7\u54c1\u5207\u53e3",
  positioningWedge: "\u7b80\u5386\u5148\u884c\uff0c\u518d\u8d70\u5b8c\u6c42\u804c\u6267\u884c",
  positioningOutcomeLabel: "\u4ea4\u4ed8\u7ed3\u679c",
  positioningOutcome: "\u4ece\u96f6\u6563\u7d20\u6750\u5230\u53ef\u8ffd\u8e2a\u6295\u9012",
  previewLabel: "\u6838\u5fc3\u8f93\u51fa",
  preview1: "\u7b80\u5386\u8bca\u65ad",
  preview2: "JD \u5bf9\u9f50",
  preview3: "\u6539\u5199\u5019\u9009",
  preview4: "\u884c\u52a8\u961f\u5217",
  studioEyebrow: "\u7b80\u5386\u5b9e\u9a8c\u5ba4",
  studioTitle: "\u7b80\u5386\u662f\u7b2c\u4e00\u4e2a\u6218\u573a",
  studioBody:
    "\u8f93\u5165\u76ee\u6807\u5c97\u4f4d\u3001JD \u548c\u96f6\u6563\u5b66\u751f\u7ecf\u5386\uff0c\u7cfb\u7edf\u4f1a\u8fd4\u56de\u8bca\u65ad\u3001\u5173\u952e\u8bcd\u7f3a\u53e3\u3001\u6539\u5199\u65b9\u5411\u548c\u4e0b\u4e00\u6b65\u6267\u884c\u961f\u5217\u3002",
  dashboardEyebrow: "\u5019\u9009\u4eba\u5de5\u4f5c\u53f0",
  dashboardTitle: "\u4e00\u4e2a\u5b66\u751f\uff0c\u4e00\u4e2a\u6c42\u804c\u64cd\u4f5c\u53f0",
  dashboardBody:
    "\u5019\u9009\u4eba\u753b\u50cf\u3001\u76ee\u6807\u5c97\u4f4d\u3001\u7b80\u5386\u7248\u672c\u3001\u5c97\u4f4d\u673a\u4f1a\u3001\u6295\u9012\u548c\u53cd\u9988\u8bb0\u5fc6\u653e\u5728\u540c\u4e00\u4e2a\u6267\u884c\u56de\u8def\u91cc\u3002",
  operationsEyebrow: "\u4fe1\u53f7\u5f55\u5165",
  operationsTitle: "\u628a\u6821\u56ed\u4fe1\u53f7\u53d8\u6210\u62db\u8058\u8bc1\u636e",
  operationsBody:
    "\u5c11\u586b\u8868\uff0c\u591a\u63d0\u70bc\u3002\u628a\u8bfe\u8bbe\u3001\u6bd4\u8d5b\u3001\u793e\u56e2\u3001\u5b9e\u4e60\u548c\u6295\u9012\u53cd\u9988\u8f6c\u6210\u80fd\u88ab\u4f01\u4e1a\u8bc6\u522b\u7684\u80fd\u529b\u8bc1\u636e\u3002",
  opportunitiesEyebrow: "\u5c97\u4f4d\u673a\u4f1a",
  opportunitiesTitle: "\u4e0d\u662f\u6bcf\u4e2a\u5c97\u4f4d\u90fd\u503c\u5f97\u82b1\u540c\u6837\u529b\u6c14",
  opportunitiesBody:
    "\u5bf9\u5c97\u4f4d\u505a\u5339\u914d\u8bc4\u5206\uff0c\u6807\u51fa\u98ce\u9669\u548c\u7f3a\u53e3\uff0c\u63a8\u8350\u6700\u5408\u9002\u7684\u7b80\u5386\u7248\u672c\uff0c\u518d\u8f6c\u6210\u53ef\u8ffd\u8e2a\u6295\u9012\u3002",
  workspaceKicker: "\u5019\u9009\u4eba",
  modulesKicker: "\u80fd\u529b\u6a21\u5757",
  targetsKicker: "\u76ee\u6807\u5c97\u4f4d",
  resumeVersionsKicker: "\u7b80\u5386\u7248\u672c",
  profileFormKicker: "\u5019\u9009\u4eba\u753b\u50cf",
  targetFormKicker: "\u6c42\u804c\u5b9a\u4f4d",
  resumeVersionFormKicker: "\u7b80\u5386\u64cd\u4f5c",
  applicationFormKicker: "\u6295\u9012\u8bb0\u5f55",
  opportunityFormKicker: "\u5bfc\u5165\u5c97\u4f4d",
  opportunityListKicker: "\u63a8\u8350\u961f\u5217",
  fieldFullName: "\u59d3\u540d",
  fieldTargetTitle: "\u4e3b\u76ee\u6807\u5c97\u4f4d",
  fieldTargetMarkets: "\u76ee\u6807\u5e02\u573a",
  fieldStrengths: "\u6838\u5fc3\u4f18\u52bf",
  fieldTargetRole: "\u5c97\u4f4d\u540d\u79f0",
  fieldTargetMarket: "\u5e02\u573a",
  fieldSeniority: "\u7ea7\u522b",
  fieldPriorities: "\u4f18\u5148\u9879",
  fieldResumeLabel: "\u7248\u672c\u6807\u7b7e",
  fieldResumeStatus: "\u72b6\u6001",
  fieldResumeFocus: "\u805a\u7126\u65b9\u5411",
  fieldResumeMarket: "\u9002\u7528\u5e02\u573a",
  fieldCompany: "\u516c\u53f8",
  fieldApplicationRole: "\u5c97\u4f4d",
  fieldApplicationStage: "\u9636\u6bb5",
  fieldNextStep: "\u4e0b\u4e00\u6b65",
  fieldOpportunityCompany: "\u516c\u53f8",
  fieldOpportunityTitle: "\u5c97\u4f4d\u540d\u79f0",
  fieldOpportunityMarket: "\u5e02\u573a",
  fieldOpportunityLocation: "\u5730\u70b9",
  fieldOpportunitySource: "\u6765\u6e90",
  fieldOpportunityDescription: "\u5c97\u4f4d\u63cf\u8ff0",
  fieldMarket: "\u76ee\u6807\u5e02\u573a",
  fieldTone: "\u8bed\u6c14\u504f\u597d",
  fieldRole: "\u76ee\u6807\u5c97\u4f4d",
  fieldResume: "\u7b80\u5386\u7247\u6bb5",
  fieldJd: "JD \u7247\u6bb5",
  saveProfile: "\u4fdd\u5b58\u753b\u50cf",
  addTarget: "\u65b0\u589e\u76ee\u6807",
  addResumeVersion: "\u65b0\u589e\u7b80\u5386\u7248\u672c",
  trackApplication: "\u8bb0\u5f55\u6295\u9012",
  scoreOpportunity: "\u5c97\u4f4d\u8bc4\u5206",
  applySuggested: "\u52a0\u5165\u6295\u9012",
  runPreview: "\u8fd0\u884c\u5206\u6790",
  commandDeck: "\u6307\u4ee4\u9762\u677f",
  workbenchInput: "\u95ef\u5173\u586b\u5199",
  liveStatus: "\u53ef\u7f16\u8f91",
  saveWorkbenchVersion: "\u4fdd\u5b58\u7248\u672c",
  generateWorkbenchDocument: "\u751f\u6210\u7b80\u5386\u6587\u4ef6",
  formatLatex: "LaTeX .tex",
  formatDocx: "Word .docx",
  loadSample: "\u8f7d\u5165\u6837\u4f8b",
  commandLog: "\u6267\u884c\u65e5\u5fd7",
  signalMatrix: "\u7b80\u5386\u4f53\u68c0",
  diagnosis: "\u8bca\u65ad\u7ed3\u679c",
  keywordStack: "\u5173\u952e\u8bcd\u6808",
  matchedKeywords: "\u5df2\u547d\u4e2d",
  missingKeywords: "\u5f85\u8865\u8db3",
  focusAreas: "\u6539\u8fdb\u91cd\u70b9",
  rewriteCandidates: "\u6539\u5199\u5019\u9009",
  nextActions: "\u4e0b\u4e00\u6b65",
  generationPlan: "\u751f\u6210\u8ba1\u5212",
  generationResult: "\u751f\u6210\u7ed3\u679c",
  rawIntake: "\u539f\u59cb\u7d20\u6750\u5f55\u5165",
  rawIntakeCopy: "\u628a\u6bd4\u8d5b\u3001\u8bfe\u8bbe\u3001\u793e\u56e2\u548c\u5b9e\u4e60\u7247\u6bb5\u5148\u6574\u7406\u6210\u4e00\u4efd\u7b80\u5386\u6bcd\u7248\u3002",
  education: "\u5b66\u6821",
  major: "\u4e13\u4e1a",
  graduationCycle: "\u6bd5\u4e1a\u65f6\u95f4",
  messyRawMaterials: "\u96f6\u6563\u7ecf\u5386\u7d20\u6750",
  createFirstDraft: "\u751f\u6210\u7b2c\u4e00\u7248",
  feedbackLoop: "\u6295\u9012\u53cd\u9988",
  result: "\u7ed3\u679c",
  notes: "\u5907\u6ce8",
  recordFeedback: "\u8bb0\u5f55\u53cd\u9988",
  batchOpportunities: "\u6279\u91cf\u5c97\u4f4d",
  runBatchRanking: "\u8fd0\u884c\u6279\u91cf\u6392\u5e8f",
  metricJdMatch: "JD \u5339\u914d",
  metricEvidence: "\u8bc1\u636e\u529b",
  metricReadability: "\u53ef\u8bfb\u6027",
  metricAtsSafety: "ATS \u5b89\u5168",
  before: "\u539f\u59cb\u8868\u8fbe",
  after: "\u6539\u5199\u540e",
  noGeneratedFile: "\u8fd8\u6ca1\u6709\u751f\u6210\u6587\u4ef6\u3002\u5148\u4fdd\u5b58\u7248\u672c\uff0c\u6216\u76f4\u63a5\u7528\u5f53\u524d\u5de5\u4f5c\u53f0\u72b6\u6001\u751f\u6210\u7b80\u5386\u3002",
  generatedStatus: "\u72b6\u6001\uff1a\u5df2\u751f\u6210\uff0c\u5e76\u5173\u8054\u5230\u6700\u65b0\u7b80\u5386\u7248\u672c\u3002",
  downloadFile: "\u4e0b\u8f7d\u6587\u4ef6",
  generatedFileReady: "\u7b80\u5386\u6587\u4ef6\u5df2\u751f\u6210",
  outputPath: "\u8f93\u51fa\u8def\u5f84",
  suggestion: "\u5efa\u8bae",
  failedStatus: "\u72b6\u6001\uff1a\u751f\u6210\u5931\u8d25",
  errorLabel: "\u9519\u8bef",
  emptyOpportunitiesTitle: "\u8fd8\u6ca1\u6709\u5c97\u4f4d\u8bc4\u5206",
  emptyOpportunitiesBody: "\u5bfc\u5165\u4e00\u4e2a\u5c97\u4f4d\uff0c\u6216\u8fd0\u884c\u6279\u91cf\u6392\u5e8f\uff0c\u5f00\u59cb\u5efa\u7acb\u4f60\u7684\u673a\u4f1a\u961f\u5217\u3002",
  emptyBoardTitle: "\u673a\u4f1a\u9762\u677f\u8fd8\u662f\u7a7a\u7684",
  emptyBoardBody: "\u5bfc\u5165\u5e76\u8bc4\u5206\u540e\uff0c\u6700\u503c\u5f97\u6295\u5165\u7684\u5c97\u4f4d\u4f1a\u51fa\u73b0\u5728\u8fd9\u91cc\u3002",
  resumeLabel: "\u7b80\u5386",
  missingSignalLabel: "\u4e2a\u7f3a\u5931\u4fe1\u53f7",
  riskFlagLabel: "\u4e2a\u98ce\u9669\u6807\u8bb0",
  savingVersion: "\u6b63\u5728\u4fdd\u5b58...",
  generatingFile: "\u6b63\u5728\u751f\u6210...",
  orbitCore: "\u6c42\u804c\u6267\u884c\u56de\u8def\u5df2\u5c31\u7eea",
  orbitResume: "\u8bca\u65ad / \u6539\u5199 / \u5bfc\u51fa",
  orbitMatch: "\u5173\u952e\u8bcd / \u8bc1\u636e / \u7f3a\u53e3",
  orbitDeploy: "\u7248\u672c / docx / \u53ef\u6295\u9012",
  orbitLoop: "\u7ed3\u679c / \u9762\u8bd5 / \u518d\u5b9a\u4f4d",
  systemModeLabel: "\u7cfb\u7edf\u6a21\u5f0f",
  primaryPathLabel: "\u4e3b\u8def\u5f84",
  primaryPathValue: "\u7b80\u5386 -> JD -> \u6295\u9012",
  systemStatusLabel: "\u72b6\u6001",
  systemStatusValue: "\u5b9e\u65f6 / \u53ef\u7f16\u8f91",
  marketUs: "\u7f8e\u56fd",
  marketUk: "\u82f1\u56fd",
  marketEu: "\u6b27\u76df",
  marketApac: "\u4e9a\u592a",
  marketRemote: "\u8fdc\u7a0b\u4f18\u5148",
  tonePrecise: "\u7cbe\u51c6\u514b\u5236",
  toneConfident: "\u81ea\u4fe1\u6e05\u6670",
  toneTechnical: "\u6280\u672f\u5bfc\u5411",
  fieldExactRoleNote: "\u5c3d\u91cf\u5199\u51c6\u76ee\u6807\u5c97\u4f4d\uff0c\u6bd4\u5982\u300c\u540e\u7aef\u5f00\u53d1\u5de5\u7a0b\u5e08\u300d\u6216\u300c\u7b97\u6cd5\u5b9e\u4e60\u751f\u300d\u3002",
  fieldResumeNote: "\u53ef\u4ee5\u7c98\u8d34\u8bfe\u8bbe\u3001\u6bd4\u8d5b\u3001\u9879\u76ee\u548c\u5b9e\u4e60\u7684\u7c97\u7cd9\u8868\u8fbe\uff0c\u4e0d\u9700\u8981\u5148\u5199\u5b8c\u7f8e\u3002",
  fieldJdNote: "\u628a JD \u91cc\u7684\u804c\u8d23\u3001\u8981\u6c42\u3001\u52a0\u5206\u9879\u7c98\u8d34\u8fdb\u6765\uff0c\u7cfb\u7edf\u4f1a\u627e\u4fe1\u53f7\u5dee\u3002",
  rawIntakeNote: "\u628a\u6bd4\u8d5b\u3001\u793e\u56e2\u3001\u8bfe\u8bbe\u3001\u5b9e\u4e60\u3001\u81ea\u5b66\u7ecf\u5386\u90fd\u5148\u4e22\u8fdb\u6765\uff0c\u6211\u4eec\u518d\u4e00\u8d77\u6253\u78e8\u3002",
  placeholderEducation: "\u6e05\u534e\u5927\u5b66",
  placeholderMajor: "\u8ba1\u7b97\u673a\u79d1\u5b66\u4e0e\u6280\u672f",
  placeholderGraduation: "2026 \u5c4a",
  placeholderFullName: "\u9648\u540c\u5b66",
  placeholderTargetTitle: "\u540e\u7aef\u5f00\u53d1\u5de5\u7a0b\u5e08",
  placeholderTargetMarkets: "\u4e92\u8054\u7f51\u5927\u5382, AI \u521b\u4e1a\u516c\u53f8, \u8fdc\u7a0b",
  placeholderStrengths: "Python, \u5de5\u7a0b\u5316, \u9879\u76ee\u63a8\u8fdb",
  placeholderTargetRole: "\u5e73\u53f0\u5f00\u53d1\u5de5\u7a0b\u5e08",
  placeholderTargetMarket: "\u5317\u4eac / \u4e0a\u6d77 / \u8fdc\u7a0b",
  placeholderSeniority: "\u6821\u62db / \u5b9e\u4e60 / \u521d\u7ea7",
  placeholderPriorities: "\u5de5\u7a0b\u80fd\u529b, \u7cfb\u7edf\u8bbe\u8ba1, \u7a33\u5b9a\u6027",
  placeholderResumeLabel: "\u6821\u62db\u540e\u7aef\u5b9a\u5236 v1",
  placeholderResumeStatus: "\u53ef\u6295\u9012",
  placeholderResumeFocus: "Python, \u8bfe\u8bbe\u9879\u76ee, \u91cf\u5316\u6210\u679c",
  placeholderResumeMarket: "\u56fd\u5185\u6821\u62db",
  placeholderApplicationCompany: "\u5b57\u8282\u8df3\u52a8",
  placeholderApplicationRole: "\u540e\u7aef\u5f00\u53d1\u5de5\u7a0b\u5e08",
  placeholderApplicationStage: "\u7b80\u5386\u5b9a\u5236\u4e2d",
  placeholderApplicationNextStep: "\u4eca\u665a\u5b8c\u6210\u7b80\u5386\u5e76\u6295\u9012",
  placeholderFeedbackCompany: "\u5b57\u8282\u8df3\u52a8",
  placeholderFeedbackRole: "\u540e\u7aef\u5f00\u53d1\u5de5\u7a0b\u5e08",
  placeholderFeedbackResult: "\u7b14\u8bd5 / \u9762\u8bd5 / \u62d2\u4fe1 / Offer",
  placeholderFeedbackNotes: "\u4e00\u9762\u88ab\u95ee\u5230\u7cfb\u7edf\u8bbe\u8ba1\uff0c\u7b54\u5f97\u4e0d\u591f\u6df1\u3002",
  placeholderOpportunityCompany: "\u963f\u91cc\u4e91",
  placeholderOpportunityTitle: "\u540e\u7aef\u5f00\u53d1\u5de5\u7a0b\u5e08",
  placeholderOpportunityMarket: "\u56fd\u5185\u6821\u62db",
  placeholderOpportunityLocation: "\u676d\u5dde / \u5317\u4eac",
  placeholderOpportunitySource: "\u5b98\u7f51\u6821\u62db",
  placeholderBatchOpportunity: "[{\"company\":\"\u817e\u8baf\",\"title\":\"\u540e\u7aef\u5f00\u53d1\u5de5\u7a0b\u5e08\",\"market\":\"\u56fd\u5185\u6821\u62db\",\"location\":\"\u6df1\u5733 / \u5317\u4eac\",\"description\":\"\u8981\u6c42 Python/Go/Java \u540e\u7aef\u57fa\u7840\uff0c\u719f\u6089\u6570\u636e\u5e93\u3001\u7f13\u5b58\u548c\u7cfb\u7edf\u7a33\u5b9a\u6027\u3002\"}]",
  opportunityListCopy: "\u5148\u7b97\u6e05\u695a\u503c\u4e0d\u503c\u5f97\u6295\uff0c\u518d\u628a\u771f\u6b63\u6709\u4ef7\u503c\u7684\u5c97\u4f4d\u53d8\u6210\u884c\u52a8\u3002",
  emptyToken: "\u6682\u65e0",
  commandWaiting: "\u5148\u5b8c\u6210\u5de6\u4fa7\u95ef\u5173\uff0c\u8fd0\u884c\u540e\u8fd9\u91cc\u4f1a\u7ed9\u51fa AI \u6253\u78e8\u5efa\u8bae\u3002",
  unavailable: "\u6682\u4e0d\u53ef\u7528",
  unknownGenerationError: "\u672a\u77e5\u751f\u6210\u9519\u8bef",
  resumeTbd: "\u5f85\u786e\u5b9a",
  roleLabel: "\u5c97\u4f4d",
  sourceLabel: "\u6765\u6e90",
  fileLabel: "\u6587\u4ef6",
  noNextStep: "\u8fd8\u6ca1\u6709\u8bb0\u5f55\u4e0b\u4e00\u6b65\u3002",
  zhSampleOpportunityDescription: "\u8981\u6c42\u719f\u6089 Python/Java/Go \u4efb\u4e00\u540e\u7aef\u6280\u672f\u6808\uff0c\u7406\u89e3\u6570\u636e\u5e93\u3001\u7f13\u5b58\u3001\u6d88\u606f\u961f\u5217\u548c\u7cfb\u7edf\u7a33\u5b9a\u6027\uff0c\u80fd\u5728\u5bfc\u5e08\u5e26\u9886\u4e0b\u5b8c\u6210\u6a21\u5757\u8bbe\u8ba1\u4e0e\u95ee\u9898\u6392\u67e5\u3002",
  zhSampleRawIntake: "\u6bd4\u8d5b\uff1aACM \u6821\u961f\u8bad\u7ec3\uff0c\u4e3b\u8981\u590d\u76d8\u56fe\u8bba\u548c DP \u9898\u578b\u3002\n\u8bfe\u8bbe\uff1a\u7528 Python + FastAPI \u505a\u6821\u56ed\u62db\u65b0\u5c0f\u7a0b\u5e8f\u540e\u7aef\uff0c\u652f\u6301 300+ \u5b66\u751f\u62a5\u540d\u3002\n\u793e\u56e2\uff1a\u7ec4\u7ec7\u6280\u672f\u5206\u4eab\u4f1a\uff0c\u8d1f\u8d23\u6d41\u7a0b\u3001\u5ba3\u4f20\u548c\u62a5\u540d\u534f\u8c03\u3002",
};

Object.assign(baseMessages, {
  pageTitle: "Resume Copilot | Resume Lab",
  brandName: "Resume Copilot",
  brandMark: "RC",
  heroCommandPreview: "> start.resume\n> paste.experience\n> add.target_role\n> generate.version",
  homeStep1: "Paste your rough experience",
  homeStep2: "Add the target role or JD",
  homeStep3: "Get a better resume version",
  homeCardKicker: "Today's mission",
  homeCardTitle: "Make one resume good enough to send.",
  homeCardBody: "No account setup. No complicated dashboard first. Start with the material you already have.",
  homeInputLabel: "Input",
  homeInputValue: "rough experience + target role",
  homeOutputLabel: "Output",
  homeOutputValue: "diagnosis + rewrite + resume file",
  homeProofLabel: "Best first use case",
  homeProofValue: "Help me polish my own resume today",
  advancedSettings: "Advanced settings",
  questKicker: "Resume Quest",
  questPageEyebrow: "Resume Quest",
  questPageTitle: "Choose a discipline, answer three questions, generate your resume.",
  questBack: "Back",
  questNext: "Next",
  questRun: "Generate resume",
  manualEditor: "Review or fine-tune source material",
  livePreview: "Live Resume Preview",
  previewTarget: "Target",
  previewEmpty: "Answer this level and it will appear here.",
  modulePlanLabel: "Module map",
  questDiscipline: "Choose your discipline",
  disciplineEngineering: "Engineering / CS",
  disciplineBusiness: "Business / Operations",
  disciplineDesign: "Design / Media",
  disciplineHumanities: "Humanities / Social Science",
  disciplineEducation: "Education / Social Impact",
  disciplineResearch: "Research / Graduate School",
  orbitCoreTitle: "RC / LAB",
  orbitResumeTitle: "Resume Lab",
  orbitMatchTitle: "JD Match",
  orbitDeployTitle: "Deploy",
  orbitLoopTitle: "Feedback Loop",
  systemModeValue: "candidate.os",
  templateHintLabel: "Template",
  pagePreferenceLabel: "Page plan",
  filenameStemLabel: "Filename",
  summaryFocusLabel: "Summary focus",
  highlightStrategyLabel: "Highlight strategy",
  noSummaryFocus: "No summary focus available.",
  noHighlightStrategy: "No highlight strategy available.",
  templateTechModern: "Tech modern",
  templateManagement: "Management",
  templateMinimal: "Minimal",
  templateFreshGraduate: "Fresh graduate",
  templateSelectLabel: "Choose a resume template",
  aiOptimization: "AI Suggestions",
  pageOnePage: "One page",
  pageAuto: "Auto",
  fallbackCandidate: "Primary Candidate",
  fallbackTargetRole: "Target Role",
  fallbackGlobal: "Global",
  sourceManual: "manual",
});

Object.assign(zhMessages, {
  pageTitle: "\u6c42\u804c\u6267\u884c\u5668 | \u7b80\u5386\u5b9e\u9a8c\u5ba4",
  brandName: "\u6c42\u804c\u6267\u884c\u5668",
  brandMark: "\u7b80",
  heroTitle: "\u628a\u96f6\u6563\u7ecf\u5386\uff0c\u53d8\u6210\u4eca\u5929\u5c31\u80fd\u6295\u7684\u7b80\u5386",
  heroBody: "\u5148\u4e0d\u505a\u590d\u6742\u6c42\u804c\u7cfb\u7edf\u3002\u4f60\u53ea\u9700\u8981\u7c98\u8d34\u7ecf\u5386\u548c\u76ee\u6807\u5c97\u4f4d\uff0c\u7cfb\u7edf\u5e2e\u4f60\u8bca\u65ad\u3001\u6539\u5199\u3001\u751f\u6210\u4e00\u4efd\u66f4\u53ef\u6295\u9012\u7684\u7b80\u5386\u3002",
  heroPrimary: "\u5f00\u59cb\u505a\u7b80\u5386",
  heroSecondary: "\u8fdb\u5165\u7b80\u5386\u95ef\u5173",
  homeStep1: "\u7c98\u8d34\u7c97\u7cd9\u7ecf\u5386",
  homeStep2: "\u586b\u5165\u76ee\u6807\u5c97\u4f4d",
  homeStep3: "\u5f97\u5230\u4e00\u4efd\u66f4\u597d\u7684\u7b80\u5386",
  homeCardKicker: "\u4eca\u5929\u53ea\u505a\u4e00\u4ef6\u4e8b",
  homeCardTitle: "\u628a\u4e00\u4efd\u7b80\u5386\u6539\u5230\u80fd\u6295\u9012",
  homeCardBody: "\u4e0d\u5148\u6ce8\u518c\uff0c\u4e0d\u5148\u914d\u7f6e\u4e00\u5806\u4fe1\u606f\uff0c\u76f4\u63a5\u4ece\u4f60\u624b\u5934\u5df2\u7ecf\u6709\u7684\u7d20\u6750\u5f00\u59cb\u3002",
  homeInputLabel: "\u4f60\u7ed9\u6211",
  homeInputValue: "\u96f6\u6563\u7ecf\u5386 + \u76ee\u6807\u5c97\u4f4d",
  homeOutputLabel: "\u6211\u8fd4\u56de",
  homeOutputValue: "\u8bca\u65ad + \u6539\u5199 + \u7b80\u5386\u6587\u4ef6",
  homeProofLabel: "\u6700\u9002\u5408\u7684\u7b2c\u4e00\u4e2a\u573a\u666f",
  homeProofValue: "\u5148\u5e2e\u6211\u628a\u81ea\u5df1\u7684\u7b80\u5386\u505a\u597d",
  advancedSettings: "\u9ad8\u7ea7\u8bbe\u7f6e",
  questKicker: "\u7b80\u5386\u95ef\u5173",
  questPageEyebrow: "\u7b80\u5386\u95ef\u5173",
  questPageTitle: "\u9009\u5b66\u79d1\uff0c\u7b54\u4e09\u5173\uff0c\u751f\u6210\u4e00\u4efd\u66f4\u80fd\u6295\u7684\u7b80\u5386",
  questBack: "\u4e0a\u4e00\u5173",
  questNext: "\u4e0b\u4e00\u5173",
  questRun: "\u751f\u6210\u7b80\u5386",
  manualEditor: "\u67e5\u770b\u6216\u5fae\u8c03\u7d20\u6750",
  livePreview: "\u5b9e\u65f6\u7b80\u5386\u9884\u89c8",
  previewTarget: "\u76ee\u6807\u5c97\u4f4d",
  previewEmpty: "\u56de\u7b54\u8fd9\u4e00\u5173\u540e\uff0c\u5185\u5bb9\u4f1a\u51fa\u73b0\u5728\u8fd9\u91cc\u3002",
  modulePlanLabel: "\u6a21\u5757\u5730\u56fe",
  questDiscipline: "\u9009\u62e9\u4f60\u7684\u5b66\u79d1\u65b9\u5411",
  disciplineEngineering: "\u5de5\u79d1 / \u8ba1\u7b97\u673a",
  disciplineBusiness: "\u5546\u79d1 / \u8fd0\u8425",
  disciplineDesign: "\u8bbe\u8ba1 / \u4f20\u5a92",
  disciplineHumanities: "\u4eba\u6587 / \u793e\u79d1",
  disciplineEducation: "\u6559\u80b2 / \u516c\u76ca",
  disciplineResearch: "\u79d1\u7814 / \u5347\u5b66",
  fieldJd: "\u804c\u4f4d\u63cf\u8ff0\u7247\u6bb5",
  metricJdMatch: "\u5c97\u4f4d\u5339\u914d",
  metricAtsSafety: "\u673a\u7b5b\u5b89\u5168",
  preview2: "\u804c\u4f4d\u63cf\u8ff0\u5bf9\u9f50",
  heroPoint2: "\u5207\u53e3\uff1a\u4ece\u7b80\u5386\u8bca\u65ad\u3001\u804c\u4f4d\u63cf\u8ff0\u5bf9\u9f50\u3001\u6587\u4ef6\u751f\u6210\u8d70\u5230\u5c97\u4f4d\u6392\u5e8f\u548c\u53cd\u9988\u5b66\u4e60",
  fieldJdNote: "\u628a\u804c\u4f4d\u63cf\u8ff0\u91cc\u7684\u804c\u8d23\u3001\u8981\u6c42\u3001\u52a0\u5206\u9879\u7c98\u8d34\u8fdb\u6765\uff0c\u7cfb\u7edf\u4f1a\u627e\u4fe1\u53f7\u5dee\u3002",
  heroCommandPreview: "> \u542f\u52a8\u7b80\u5386\u5b9e\u9a8c\u5ba4\n> \u8f7d\u5165\u5019\u9009\u4eba\u753b\u50cf\n> \u89e3\u6790\u804c\u4f4d\u63cf\u8ff0\n> \u68c0\u6d4b\u4fe1\u53f7\u7f3a\u53e3\n> \u751f\u6210\u6539\u5199\u65b9\u6848",
  orbitCoreTitle: "\u7b80\u5386\u5b9e\u9a8c\u5ba4",
  orbitResumeTitle: "\u7b80\u5386\u8bca\u65ad",
  orbitMatchTitle: "\u5c97\u4f4d\u5339\u914d",
  orbitDeployTitle: "\u751f\u6210\u6295\u9012",
  orbitLoopTitle: "\u53cd\u9988\u5faa\u73af",
  systemModeValue: "\u5019\u9009\u4eba\u64cd\u4f5c\u7cfb\u7edf",
  orbitDeploy: "\u7248\u672c / \u6587\u6863 / \u53ef\u6295\u9012",
  primaryPathValue: "\u7b80\u5386 -> \u804c\u4f4d\u63cf\u8ff0 -> \u6295\u9012",
  placeholderStrengths: "\u540e\u7aef\u5f00\u53d1, \u5de5\u7a0b\u5316, \u9879\u76ee\u63a8\u8fdb",
  placeholderResumeFocus: "\u540e\u7aef\u5f00\u53d1, \u8bfe\u8bbe\u9879\u76ee, \u91cf\u5316\u6210\u679c",
  placeholderFeedbackResult: "\u7b14\u8bd5 / \u9762\u8bd5 / \u62d2\u4fe1 / \u5f55\u7528",
  placeholderBatchOpportunity: "[{\"company\":\"\u817e\u8baf\",\"title\":\"\u540e\u7aef\u5f00\u53d1\u5de5\u7a0b\u5e08\",\"market\":\"\u56fd\u5185\u6821\u62db\",\"location\":\"\u6df1\u5733 / \u5317\u4eac\",\"description\":\"\u8981\u6c42\u540e\u7aef\u57fa\u7840\uff0c\u719f\u6089\u6570\u636e\u5e93\u3001\u7f13\u5b58\u548c\u7cfb\u7edf\u7a33\u5b9a\u6027\u3002\"}]",
  zhSampleOpportunityDescription: "\u8981\u6c42\u719f\u6089\u4e00\u95e8\u540e\u7aef\u6280\u672f\u6808\uff0c\u7406\u89e3\u6570\u636e\u5e93\u3001\u7f13\u5b58\u3001\u6d88\u606f\u961f\u5217\u548c\u7cfb\u7edf\u7a33\u5b9a\u6027\uff0c\u80fd\u5728\u5bfc\u5e08\u5e26\u9886\u4e0b\u5b8c\u6210\u6a21\u5757\u8bbe\u8ba1\u4e0e\u95ee\u9898\u6392\u67e5\u3002",
  zhSampleRawIntake: "\u6bd4\u8d5b\uff1a\u6821\u961f\u7b97\u6cd5\u8bad\u7ec3\uff0c\u4e3b\u8981\u590d\u76d8\u56fe\u8bba\u548c\u52a8\u6001\u89c4\u5212\u9898\u578b\u3002\n\u8bfe\u8bbe\uff1a\u7528\u540e\u7aef\u6846\u67b6\u505a\u6821\u56ed\u62db\u65b0\u5c0f\u7a0b\u5e8f\u670d\u52a1\u7aef\uff0c\u652f\u6301 300+ \u5b66\u751f\u62a5\u540d\u3002\n\u793e\u56e2\uff1a\u7ec4\u7ec7\u6280\u672f\u5206\u4eab\u4f1a\uff0c\u8d1f\u8d23\u6d41\u7a0b\u3001\u5ba3\u4f20\u548c\u62a5\u540d\u534f\u8c03\u3002",
  templateHintLabel: "\u6a21\u677f",
  pagePreferenceLabel: "\u9875\u6570\u7b56\u7565",
  filenameStemLabel: "\u6587\u4ef6\u540d",
  summaryFocusLabel: "\u6458\u8981\u805a\u7126",
  highlightStrategyLabel: "\u4eae\u70b9\u7b56\u7565",
  noSummaryFocus: "\u6682\u65e0\u6458\u8981\u805a\u7126\u3002",
  noHighlightStrategy: "\u6682\u65e0\u4eae\u70b9\u7b56\u7565\u3002",
  templateTechModern: "\u6280\u672f\u578b\u6a21\u677f",
  templateManagement: "\u7ba1\u7406\u578b\u6a21\u677f",
  templateMinimal: "\u6781\u7b80\u578b\u6a21\u677f",
  templateFreshGraduate: "\u5e94\u5c4a\u751f\u6a21\u677f",
  templateSelectLabel: "\u9009\u62e9\u7b80\u5386\u6a21\u677f",
  aiOptimization: "AI \u6253\u78e8\u5efa\u8bae",
  pageOnePage: "\u4e00\u9875",
  pageAuto: "\u81ea\u52a8",
  fallbackCandidate: "\u5019\u9009\u4eba",
  fallbackTargetRole: "\u76ee\u6807\u5c97\u4f4d",
  fallbackGlobal: "\u5168\u5c40",
  sourceManual: "\u624b\u52a8\u5f55\u5165",
});

const messages = {
  en: baseMessages,
  "zh-CN": { ...baseMessages, ...zhMessages },
};

function applyLanguage(locale) {
  document.documentElement.lang = locale;
  document.title = messages[locale].pageTitle || messages.en.pageTitle;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    const key = node.dataset.i18n;
    const value = messages[locale][key];
    if (value) node.textContent = value;
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    const key = node.dataset.i18nPlaceholder;
    const value = messages[locale][key];
    if (value) node.setAttribute("placeholder", value);
  });
  const commandPreview = document.getElementById("heroCommandPreview");
  if (commandPreview) commandPreview.textContent = messages[locale].heroCommandPreview;
}

function t(key) {
  const locale = document.getElementById("languageSelect")?.value || "en";
  return messages[locale][key] || messages.en[key] || key;
}

function currentLocale() {
  return document.getElementById("languageSelect")?.value || "en";
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function isZh() {
  return currentLocale() === "zh-CN";
}

const zhUiText = {
  "active": "\u8fd0\u884c\u4e2d",
  "next": "\u5f85\u542f\u52a8",
  "review": "\u5f85\u590d\u6838",
  "tracked": "\u5df2\u8ffd\u8e2a",
  "recommended": "\u63a8\u8350",
  "foundation": "\u57fa\u7840\u9636\u6bb5",
  "manual": "\u624b\u52a8\u5f55\u5165",
  "resume_lab": "\u7b80\u5386\u5b9e\u9a8c\u5ba4",
  "raw_intake": "\u539f\u59cb\u7d20\u6750\u5f55\u5165",
  "Ready": "\u53ef\u6295\u9012",
  "Draft": "\u8349\u7a3f",
  "Generated": "\u5df2\u751f\u6210",
  "In progress": "\u8fdb\u884c\u4e2d",
  "Core master resume": "\u6838\u5fc3\u6bcd\u7248\u7b80\u5386",
  "JD-tailored version": "\u5c97\u4f4d\u5b9a\u5236\u7248",
  "Student Profile Agent": "\u5b66\u751f\u753b\u50cf\u4ee3\u7406",
  "Resume Lab Agent": "\u7b80\u5386\u5b9e\u9a8c\u5ba4\u4ee3\u7406",
  "Targeting Agent": "\u5b9a\u4f4d\u4ee3\u7406",
  "Opportunity Agent": "\u5c97\u4f4d\u673a\u4f1a\u4ee3\u7406",
  "Application Agent": "\u6295\u9012\u4ee3\u7406",
  "Interview Agent": "\u9762\u8bd5\u4ee3\u7406",
  "Help one student turn messy campus experience into interviews through a repeatable resume-first job-search loop.": "\u5e2e\u4e00\u4e2a\u5b66\u751f\u901a\u8fc7\u7b80\u5386\u5148\u884c\u7684\u6c42\u804c\u56de\u8def\uff0c\u628a\u96f6\u6563\u6821\u56ed\u7ecf\u5386\u8f6c\u5316\u4e3a\u9762\u8bd5\u673a\u4f1a\u3002",
  "Captures school, major, target roles, strengths, constraints, and writing preferences.": "\u8bb0\u5f55\u5b66\u6821\u3001\u4e13\u4e1a\u3001\u76ee\u6807\u5c97\u4f4d\u3001\u4f18\u52bf\u3001\u9650\u5236\u548c\u5199\u4f5c\u504f\u597d\u3002",
  "Turns rough student materials into JD-aligned resume versions and export-ready files.": "\u628a\u7c97\u7cd9\u5b66\u751f\u7d20\u6750\u8f6c\u6210\u5bf9\u9f50\u804c\u4f4d\u63cf\u8ff0\u7684\u7b80\u5386\u7248\u672c\u548c\u53ef\u5bfc\u51fa\u6587\u4ef6\u3002",
  "Clarifies which roles deserve focus and what evidence each role needs.": "\u5224\u65ad\u54ea\u4e9b\u5c97\u4f4d\u503c\u5f97\u805a\u7126\uff0c\u4ee5\u53ca\u6bcf\u4e2a\u5c97\u4f4d\u9700\u8981\u54ea\u4e9b\u8bc1\u636e\u3002",
  "Scores roles, flags weak signals, recommends a resume version, and avoids blind mass-apply.": "\u7ed9\u5c97\u4f4d\u8bc4\u5206\uff0c\u6807\u51fa\u5f31\u4fe1\u53f7\uff0c\u63a8\u8350\u7b80\u5386\u7248\u672c\uff0c\u907f\u514d\u76f2\u76ee\u6d77\u6295\u3002",
  "Keeps applications, resume variants, next actions, and outcomes in one execution queue.": "\u628a\u6295\u9012\u3001\u7b80\u5386\u7248\u672c\u3001\u4e0b\u4e00\u6b65\u548c\u7ed3\u679c\u653e\u5230\u540c\u4e00\u4e2a\u6267\u884c\u961f\u5217\u3002",
  "Converts the strongest resume evidence into project walkthroughs and interview stories.": "\u628a\u6700\u5f3a\u7684\u7b80\u5386\u8bc1\u636e\u8f6c\u6210\u9879\u76ee\u590d\u76d8\u548c\u9762\u8bd5\u6545\u4e8b\u3002",
  "General backend positioning": "\u901a\u7528\u540e\u7aef\u5b9a\u4f4d",
  "Python + distributed systems": "\u540e\u7aef\u5f00\u53d1\u4e0e\u5206\u5e03\u5f0f\u7cfb\u7edf",
  "Tailoring": "\u7b80\u5386\u5b9a\u5236\u4e2d",
  "Interview prep": "\u9762\u8bd5\u51c6\u5907",
  "Finalize role-specific resume": "\u5b8c\u6210\u5c97\u4f4d\u5b9a\u5236\u7b80\u5386",
  "Prepare project deep-dive stories": "\u51c6\u5907\u9879\u76ee\u6df1\u6316\u6545\u4e8b",
};

function localizeText(value) {
  if (value === undefined || value === null) return "";
  const text = String(value);
  if (!isZh()) return text;
  let translated = zhUiText[text] || text;
  translated = translated
    .replaceAll("JD", "\u804c\u4f4d\u63cf\u8ff0")
    .replaceAll("ATS", "\u673a\u7b5b")
    .replaceAll("Template hint", "\u6a21\u677f")
    .replaceAll("Page preference", "\u9875\u6570\u7b56\u7565")
    .replaceAll("Filename stem", "\u6587\u4ef6\u540d")
    .replaceAll("No summary focus available.", "\u6682\u65e0\u6458\u8981\u805a\u7126\u3002")
    .replaceAll("No highlight strategy available.", "\u6682\u65e0\u4eae\u70b9\u7b56\u7565\u3002")
    .replaceAll("Role:", "\u5c97\u4f4d\uff1a")
    .replaceAll("Source:", "\u6765\u6e90\uff1a")
    .replaceAll("File:", "\u6587\u4ef6\uff1a");
  return zhUiText[translated] || translated;
}

function localizeList(items) {
  return (items || []).map(localizeText);
}

function statusText(status) {
  return localizeText(status || "");
}

function templateText(value) {
  const key = {
    tech_modern: "templateTechModern",
    management: "templateManagement",
    minimal: "templateMinimal",
    fresh_graduate: "templateFreshGraduate",
  }[value] || "";
  return key ? t(key) : localizeText(value || "tech_modern");
}

function pagePlanText(value) {
  const key = { one_page: "pageOnePage", auto: "pageAuto" }[value] || "";
  return key ? t(key) : localizeText(value || "one_page");
}

function renderList(containerId, items, renderer) {
  const node = document.getElementById(containerId);
  if (!node) return;
  node.innerHTML = (items || []).map(renderer).join("");
}

function resetForm(formId) {
  const form = document.getElementById(formId);
  if (form) form.reset();
}

function formatJoin(values) {
  return (values || []).join(" / ");
}

function tokenMarkup(items, klass = "") {
  if (!items || !items.length) {
    return `<span class="token ${klass}">${t("emptyToken")}</span>`;
  }
  return items.map((item) => `<span class="token ${klass}">${item}</span>`).join("");
}

function metricTone(value) {
  const numeric = Number(value || 0);
  if (numeric >= 75) return "high";
  if (numeric >= 50) return "mid";
  return "low";
}

function renderEmptyState(title, body) {
  return `
    <article class="empty-state">
      <strong>${title}</strong>
      <p>${body}</p>
    </article>
  `;
}

function setButtonBusy(button, busyText, task) {
  const originalText = button.textContent;
  button.disabled = true;
  button.classList.add("is-busy");
  button.textContent = busyText;
  return task.finally(() => {
    button.disabled = false;
    button.classList.remove("is-busy");
    button.textContent = originalText;
  });
}

function renderWorkbench(payload) {
  document.getElementById("studioOutput")?.classList.remove("is-empty");
  const report = payload.report || {};
  const metrics = report.metrics || {};

  const ai = payload.ai_optimization || {};
  const agentMode =
    ai.provider === "ai"
      ? "AI Resume Revision Agent 已接入"
      : "本地规则模式：请配置 AI 接口后启用真正的简历修改 Agent";
  document.getElementById("commandLog").textContent = [
    agentMode,
    ai.summary || t("commandWaiting"),
    ...(ai.improved_bullets || []).map((item) => `• ${localizeText(item)}`),
    ai.template_reason ? `\n${localizeText(ai.template_reason)}` : "",
  ]
    .filter(Boolean)
    .join("\n");

  document.getElementById("scoreMatrix").innerHTML = [
    [t("metricJdMatch"), metrics.jd_match_score],
    [t("metricEvidence"), metrics.quantified_evidence_score],
    [t("metricReadability"), metrics.readability_score],
    [t("metricAtsSafety"), metrics.ats_safety_score],
  ]
    .map(
      ([label, value]) => `
        <article class="metric-card metric-${metricTone(value)}">
          <span>${label}</span>
          <strong>${Math.round(value || 0)}</strong>
        </article>
      `,
    )
    .join("");

  renderList(
    "diagnosisList",
    localizeList(report.diagnosis || []),
    (item) => `<article class="stack-item"><strong>${item}</strong></article>`,
  );

  document.getElementById("matchedKeywords").innerHTML = tokenMarkup(
    payload.keyword_stack?.matched || [],
  );
  document.getElementById("missingKeywords").innerHTML = tokenMarkup(
    payload.keyword_stack?.missing || [],
    "missing",
  );

  renderList(
    "focusAreaList",
    localizeList(payload.focus_areas || []),
    (item) => `<article class="stack-item"><p>${item}</p></article>`,
  );

  renderList(
    "rewriteCandidateList",
    payload.rewrite_candidates || [],
    (item) => `
      <article class="rewrite-card">
        <strong>${t("before")}</strong>
        <code>${item.before || ""}</code>
        <strong>${t("after")}</strong>
        <code>${localizeText(item.after || "")}</code>
      </article>
    `,
  );

  renderList(
    "nextActionList",
    localizeList(payload.next_actions || []),
    (item) => `<article class="stack-item"><p>${item}</p></article>`,
  );

  const generationPlan = payload.generation_plan || {};
  if (templateSelect && generationPlan.template_hint) {
    templateSelect.value = generationPlan.template_hint;
    renderLivePreview();
  }
  renderList(
    "generationPlan",
    [
      `${t("templateHintLabel")}: ${templateText(generationPlan.template_hint || "tech_modern")}`,
      `${t("pagePreferenceLabel")}: ${pagePlanText(generationPlan.page_preference || "one_page")}`,
      `${t("filenameStemLabel")}: ${localizeText(generationPlan.filename_stem || "resume")}`,
      `${t("summaryFocusLabel")}: ${localizeText(generationPlan.summary_focus || t("noSummaryFocus"))}`,
      `${t("highlightStrategyLabel")}: ${localizeText(generationPlan.highlight_strategy || t("noHighlightStrategy"))}`,
    ],
    (item) => `<article class="stack-item"><p>${item}</p></article>`,
  );

  renderGenerationResult(payload.generation_result || null);
}

function downloadGeneratedFile(result) {
  if (!result?.success || !result.output_path) return;
  const link = document.createElement("a");
  link.href = `/api/download?path=${encodeURIComponent(result.output_path)}`;
  link.download = "";
  link.style.display = "none";
  document.body.appendChild(link);
  link.click();
  link.remove();
}

function generatedFileName(path) {
  return String(path || "").split(/[\\/]/).pop() || t("unavailable");
}

function renderGenerationResult(result) {
  const host = document.getElementById("generationResult");
  if (!host) return;
  if (!result) {
    host.innerHTML = `<article class="delivery-empty"><p>${t("noGeneratedFile")}</p></article>`;
  } else if (result.success) {
    const downloadUrl = `/api/download?path=${encodeURIComponent(result.output_path || "")}`;
    const suggestions = (result.suggestions || [])
      .slice(0, 3)
      .map((item) => `<li>${localizeText(item)}</li>`)
      .join("");
    host.innerHTML = `
      <article class="delivery-ready">
        <div>
          <strong>${t("generatedFileReady")}</strong>
          <p>${generatedFileName(result.output_path)} · ${result.output_format || "file"}</p>
        </div>
        <a class="button button-primary" href="${downloadUrl}" download>${t("downloadFile")}</a>
      </article>
      ${suggestions ? `<ul class="delivery-suggestions">${suggestions}</ul>` : ""}
    `;
  } else {
    host.innerHTML = `<article class="delivery-empty"><strong>${t("failedStatus")}</strong><p>${t("errorLabel")}: ${result.error || t("unknownGenerationError")}</p></article>`;
  }
}

function collectWorkbenchInput() {
  return {
    market: document.getElementById("marketSelect").value,
    tone: document.getElementById("toneSelect").value,
    discipline: questDisciplineSelect?.value || "",
    template: templateSelect?.value || "",
    output_format: document.getElementById("outputFormatSelect")?.value || "latex",
    role: document.getElementById("roleInput").value.trim(),
    resume: document.getElementById("resumeInput").value.trim(),
    jd: document.getElementById("jdInput").value.trim(),
  };
}

function renderOpportunities(opportunities) {
  renderList(
    "opportunityList",
    opportunities && opportunities.length
      ? opportunities
      : [{ empty: true, html: renderEmptyState(t("emptyOpportunitiesTitle"), t("emptyOpportunitiesBody")) }],
    (item) =>
      item.empty
        ? item.html
        : `
      <article class="stack-item">
        <div class="stack-head">
          <strong>${item.company}</strong>
          <span class="status-pill status-${item.status === "tracked" ? "active" : item.status === "review" ? "foundation" : "next"}">${statusText(item.status)}</span>
        </div>
        <p>${localizeText(item.title)} / ${localizeText(item.market)}${item.location ? ` / ${localizeText(item.location)}` : ""}</p>
      </article>
    `,
  );

  const board = document.getElementById("opportunityBoard");
  board.innerHTML =
    (opportunities || [])
      .slice(0, 6)
      .map(
        (item) => `
      <div class="stack-item">
        <div class="stack-head">
          <strong>${localizeText(item.company)} / ${localizeText(item.title)}</strong>
          <span class="status-pill status-${item.status === "tracked" ? "active" : item.status === "review" ? "foundation" : "next"}">${Math.round(item.fit_score || 0)}</span>
        </div>
        <p>${localizeList(item.score_report?.match_reasons || item.match_reasons || []).join(" ")}</p>
        <p>${item.recommended_resume_version ? `${t("resumeLabel")}: ${localizeText(item.recommended_resume_version)}` : `${t("resumeLabel")}: ${t("resumeTbd")}`}</p>
        <p class="stack-meta">${(item.missing_signals || []).length} ${t("missingSignalLabel")} / ${(item.risk_flags || []).length} ${t("riskFlagLabel")}</p>
        <button class="button button-ghost full-width opportunity-apply" data-company="${item.company}" data-title="${item.title}">
          ${messages[document.getElementById("languageSelect").value].applySuggested}
        </button>
      </div>
    `,
      )
      .join("") ||
    renderEmptyState(t("emptyBoardTitle"), t("emptyBoardBody"));

  document.querySelectorAll(".opportunity-apply").forEach((button) => {
    button.addEventListener("click", async () => {
      const snapshot = await postJson("/api/opportunities/apply", {
        company: button.dataset.company,
        title: button.dataset.title,
      });
      renderDashboard(snapshot);
    });
  });
}

function renderDashboard(payload) {
  document.getElementById("workspaceTitle").textContent = localizeText(payload.profile.full_name);
  document.getElementById("workspaceNorthStar").textContent = localizeText(payload.north_star);
  document.getElementById("workspaceMarkets").innerHTML = (payload.profile.target_markets || [])
    .map((market) => `<span class="chip">${localizeText(market)}</span>`)
    .join("");

  document.getElementById("profileFullName").value = payload.profile.full_name || "";
  document.getElementById("profileTargetTitle").value = payload.profile.target_title || "";
  document.getElementById("profileTargetMarkets").value = formatJoin(payload.profile.target_markets);
  document.getElementById("profileStrengths").value = formatJoin(payload.profile.strengths);

  renderList("moduleList", payload.modules || [], (item) => `
    <article class="stack-item">
      <div class="stack-head">
        <strong>${localizeText(item.name)}</strong>
        <span class="status-pill status-${item.status}">${statusText(item.status)}</span>
      </div>
      <p>${localizeText(item.description)}</p>
    </article>
  `);

  renderList("targetList", payload.targets || [], (item) => `
    <article class="stack-item">
      <div class="stack-head">
        <strong>${localizeText(item.title)}</strong>
        <span>${localizeText(item.market)}</span>
      </div>
      <p>${localizeText(item.seniority)} / ${formatJoin(localizeList(item.priorities))}</p>
    </article>
  `);

  renderList("resumeVersionList", payload.resume_versions || [], (item) => `
    <article class="stack-item">
      <div class="stack-head">
        <strong>${localizeText(item.label)}</strong>
        <span class="status-pill status-active">${statusText(item.status)}</span>
      </div>
      <p>${localizeText(item.market)} / ${localizeText(item.focus)}</p>
      <p class="stack-meta">${item.role ? `${t("roleLabel")}: ${localizeText(item.role)}` : `${t("sourceLabel")}: ${localizeText(item.source || t("sourceManual"))}`}</p>
      <p class="stack-meta mono">${item.output_path ? `${t("fileLabel")}: ${item.output_path}` : `${t("sourceLabel")}: ${localizeText(item.source || t("sourceManual"))}`}</p>
    </article>
  `);

  renderOpportunities(payload.opportunities || []);

  renderList("applicationList", payload.applications || [], (item) => `
    <article class="stack-item">
      <div class="stack-head">
        <strong>${localizeText(item.company)}</strong>
        <span class="status-pill status-next">${localizeText(item.stage)}</span>
      </div>
      <p>${localizeText(item.role)}</p>
      <p class="stack-meta">${localizeText(item.next_step || t("noNextStep"))}</p>
    </article>
  `);

  renderList("interviewList", payload.interviews || [], (item) => `
    <article class="stack-item">
      <div class="stack-head">
        <strong>${localizeText(item.topic)}</strong>
        <span class="status-pill status-foundation">${localizeText(item.status)}</span>
      </div>
      <p>${localizeText(item.focus)}</p>
    </article>
  `);

  renderList(
    "memoryList",
    payload.memory_notes || [],
    (item) => `<article class="stack-item"><p>${localizeText(item)}</p></article>`,
  );
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error(`HTTP ${response.status}`);
  return response.json();
}

async function loadDashboard() {
  try {
    const response = await fetch("/api/dashboard");
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    renderDashboard(await response.json());
  } catch (error) {
    const isZh = document.getElementById("languageSelect").value === "zh-CN";
    renderDashboard({
      profile: {
        full_name: isZh ? "\u9648\u540c\u5b66" : t("fallbackCandidate"),
        target_title: isZh ? "\u540e\u7aef\u5f00\u53d1\u5de5\u7a0b\u5e08" : "Senior Backend Engineer",
        target_markets: isZh ? ["\u56fd\u5185\u6821\u62db", "AI \u521b\u4e1a\u516c\u53f8"] : ["US", "Remote"],
        strengths: isZh ? ["Python", "\u5de5\u7a0b\u5316", "\u9879\u76ee\u63a8\u8fdb"] : ["Distributed systems", "Python backend"],
      },
      north_star: isZh
        ? "\u5e2e\u4e00\u4e2a\u771f\u5b9e\u5019\u9009\u4eba\u4ece\u7b80\u5386\u6253\u78e8\u8d70\u5230\u5b8c\u6574\u6c42\u804c\u6267\u884c\u3002"
        : "Help one student turn messy campus experience into interviews through a repeatable resume-first job-search loop.",
      modules: [],
      targets: [],
      resume_versions: [],
      opportunities: [],
      applications: [],
      interviews: [],
      memory_notes: [isZh ? "\u540e\u7aef\u6682\u4e0d\u53ef\u7528\uff1a\u5f53\u524d\u663e\u793a\u5907\u7528\u5de5\u4f5c\u53f0\u3002" : "Backend unavailable: showing fallback workspace."],
    });
  }
}

function loadWorkbenchSample() {
  const isZh = document.getElementById("languageSelect").value === "zh-CN";
  if (document.getElementById("languageSelect").value === "zh-CN") {
    document.getElementById("roleInput").value = "\u540e\u7aef\u5f00\u53d1\u5de5\u7a0b\u5e08";
    document.getElementById("resumeInput").value =
      "\u8bfe\u8bbe\u9879\u76ee\uff1a\u7528\u540e\u7aef\u6846\u67b6\u642d\u5efa\u6821\u56ed\u62db\u65b0\u5c0f\u7a0b\u5e8f\u670d\u52a1\u7aef\uff0c\u652f\u6301 300+ \u5b66\u751f\u62a5\u540d\u3002\n\u6bd4\u8d5b\u7ecf\u5386\uff1a\u53c2\u4e0e\u6821\u961f\u7b97\u6cd5\u8bad\u7ec3\uff0c\u8d1f\u8d23\u56fe\u8bba\u548c\u52a8\u6001\u89c4\u5212\u9898\u578b\u590d\u76d8\u3002\n\u793e\u56e2\u7ecf\u5386\uff1a\u7ec4\u7ec7\u6821\u56ed\u6280\u672f\u5206\u4eab\u4f1a\uff0c\u534f\u8c03\u573a\u5730\u3001\u5ba3\u4f20\u548c\u62a5\u540d\u6d41\u7a0b\u3002";
    document.getElementById("jdInput").value =
      "\u8981\u6c42\u624e\u5b9e\u7684\u8ba1\u7b97\u673a\u57fa\u7840\uff0c\u719f\u6089 Python/Java/C++ \u4efb\u4e00\u6280\u672f\u6808\uff0c\u6709\u540e\u7aef\u9879\u76ee\u7ecf\u9a8c\uff0c\u80fd\u8bf4\u6e05\u7cfb\u7edf\u8bbe\u8ba1\u601d\u8def\uff0c\u5177\u5907\u826f\u597d\u7684\u6c9f\u901a\u548c\u5b66\u4e60\u80fd\u529b\u3002";
    return;
  }
  document.getElementById("roleInput").value = "Senior Backend Engineer";
  document.getElementById("resumeInput").value =
    "Built Python services for analytics workflows.\nImproved release reliability and collaborated with product managers.\nMaintained APIs and deployment pipelines.";
  document.getElementById("jdInput").value =
    "Looking for a backend engineer who can design distributed systems, improve reliability, communicate with stakeholders, and mentor teammates.";
}

function loadLocalizedExamples() {
  const isZh = document.getElementById("languageSelect").value === "zh-CN";
  document.getElementById("commandLog").textContent = t("commandWaiting");
  document.getElementById("opportunityDescription").value = isZh
    ? messages["zh-CN"].zhSampleOpportunityDescription
    : messages.en.zhSampleOpportunityDescription;
  document.getElementById("intakeRawText").value = isZh
    ? messages["zh-CN"].zhSampleRawIntake
    : messages.en.zhSampleRawIntake;
}

const languageSelect = document.getElementById("languageSelect");
const resumeWorkbenchForm = document.getElementById("resumeWorkbenchForm");
const rawIntakeForm = document.getElementById("rawIntakeForm");
const profileForm = document.getElementById("profileForm");
const targetForm = document.getElementById("targetForm");
const resumeVersionForm = document.getElementById("resumeVersionForm");
const applicationForm = document.getElementById("applicationForm");
const applicationFeedbackForm = document.getElementById("applicationFeedbackForm");
const opportunityForm = document.getElementById("opportunityForm");
const questAnswer = document.getElementById("questAnswer");
const questTitle = document.getElementById("questTitle");
const questPrompt = document.getElementById("questPrompt");
const questBadge = document.getElementById("questBadge");
const questProgress = document.getElementById("questProgress");
const questChips = document.getElementById("questChips");
const questPrevButton = document.getElementById("questPrevButton");
const questNextButton = document.getElementById("questNextButton");
const questRunButton = document.getElementById("questRunButton");
const questDisciplineSelect = document.getElementById("questDisciplineSelect");
const templateSelect = document.getElementById("templateSelect");
const questModulePlan = document.getElementById("questModulePlan");
const previewRole = document.getElementById("previewRole");
const previewTemplate = document.getElementById("previewTemplate");
const previewModules = document.getElementById("previewModules");
const previewSheet = document.getElementById("previewSheet");

const questSteps = {
  en: [
    {
      fieldId: "roleInput",
      title: "Level 1: choose the target",
      prompt: "What role do you want this resume to win?",
      placeholder: "Backend Engineer Intern / Product Manager Intern / AI Engineer",
      presets: ["Backend Engineer Intern", "AI Product Manager", "Data Analyst Intern"],
    },
    {
      fieldId: "resumeInput",
      title: "Level 2: drop your raw material",
      prompt: "Paste projects, coursework, competitions, internships, clubs, or anything worth packaging.",
      placeholder: "Course project: built a campus app backend...\nCompetition: algorithm team training...\nClub: organized a tech sharing event...",
      presets: ["Course project", "Competition", "Internship", "Student club"],
    },
    {
      fieldId: "jdInput",
      title: "Level 3: add the enemy map",
      prompt: "Paste a JD, or describe what the company wants. I will match your evidence against it.",
      placeholder: "Requires Python, databases, communication, problem solving, and project experience...",
      presets: ["Campus recruitment JD", "Internship JD", "No JD yet"],
    },
  ],
  "zh-CN": [
    {
      fieldId: "roleInput",
      title: "\u7b2c 1 \u5173\uff1a\u9009\u5b9a\u76ee\u6807",
      prompt: "\u4f60\u60f3\u7528\u8fd9\u4efd\u7b80\u5386\u6295\u4ec0\u4e48\u5c97\u4f4d\uff1f\u5148\u5199\u4e00\u4e2a\u6700\u60f3\u8981\u7684\u3002",
      placeholder: "\u540e\u7aef\u5f00\u53d1\u5b9e\u4e60\u751f / AI \u4ea7\u54c1\u7ecf\u7406 / \u6570\u636e\u5206\u6790\u5b9e\u4e60\u751f",
      presets: ["\u540e\u7aef\u5f00\u53d1\u5b9e\u4e60\u751f", "AI \u4ea7\u54c1\u7ecf\u7406", "\u6570\u636e\u5206\u6790\u5b9e\u4e60\u751f"],
    },
    {
      fieldId: "resumeInput",
      title: "\u7b2c 2 \u5173\uff1a\u6295\u653e\u7d20\u6750",
      prompt: "\u628a\u8bfe\u8bbe\u3001\u9879\u76ee\u3001\u6bd4\u8d5b\u3001\u5b9e\u4e60\u3001\u793e\u56e2\u90fd\u4e22\u8fdb\u6765\uff0c\u4e0d\u9700\u8981\u5199\u5f97\u6f02\u4eae\u3002",
      placeholder: "\u8bfe\u8bbe\uff1a\u505a\u4e86\u4e00\u4e2a\u6821\u56ed\u5c0f\u7a0b\u5e8f\u540e\u7aef...\n\u6bd4\u8d5b\uff1a\u53c2\u4e0e\u7b97\u6cd5\u8bad\u7ec3...\n\u793e\u56e2\uff1a\u7ec4\u7ec7\u6280\u672f\u5206\u4eab\u4f1a...",
      presets: ["\u8bfe\u8bbe\u9879\u76ee", "\u6bd4\u8d5b\u7ecf\u5386", "\u5b9e\u4e60\u7ecf\u5386", "\u793e\u56e2\u7ecf\u5386"],
    },
    {
      fieldId: "jdInput",
      title: "\u7b2c 3 \u5173\uff1a\u653e\u5165\u5c97\u4f4d\u5730\u56fe",
      prompt: "\u7c98\u8d34 JD\uff0c\u6216\u8005\u7528\u5927\u767d\u8bdd\u5199\u4f01\u4e1a\u60f3\u8981\u4ec0\u4e48\u3002\u6211\u4f1a\u5e2e\u4f60\u627e\u5339\u914d\u548c\u7f3a\u53e3\u3002",
      placeholder: "\u8981\u6c42 Python\uff0c\u719f\u6089\u6570\u636e\u5e93\uff0c\u6709\u9879\u76ee\u7ecf\u5386\uff0c\u6c9f\u901a\u80fd\u529b\u597d...",
      presets: ["\u6821\u62db JD", "\u5b9e\u4e60 JD", "\u6682\u65e0 JD"],
    },
  ],
};

const disciplineQuestSteps = {
  en: {
    engineering: [
      {
        fieldId: "roleInput",
        title: "Engineering path: target role",
        prompt: "What engineering role are you aiming for? Include stack or direction if you know it.",
        placeholder: "Backend Engineer Intern / Embedded Systems Intern / AI Engineer",
        presets: ["Backend Engineer Intern", "Frontend Engineer Intern", "AI Engineer", "Embedded Intern"],
      },
      {
        fieldId: "resumeInput",
        title: "Engineering path: proof of building",
        prompt: "List projects, systems, algorithms, experiments, tools, scale, bugs fixed, or measurable outcomes.",
        placeholder: "Project: built a FastAPI service, designed database tables, supported 300 users...\nCoursework: OS, DB, networks...\nCompetition: algorithm training...",
        presets: ["Project + tech stack", "System design", "Coursework", "Competition", "GitHub link"],
      },
      {
        fieldId: "jdInput",
        title: "Engineering path: hiring signals",
        prompt: "Paste the JD or list required stack, engineering habits, collaboration style, and evaluation keywords.",
        placeholder: "Requires Python/Java, databases, distributed systems, debugging, ownership, communication...",
        presets: ["Tech stack", "System reliability", "Team collaboration", "Problem solving"],
      },
    ],
    business: [
      {
        fieldId: "roleInput",
        title: "Business path: target function",
        prompt: "Which function do you want: product, operations, consulting, marketing, finance, or strategy?",
        placeholder: "Product Manager Intern / Operations Intern / Strategy Analyst",
        presets: ["Product Intern", "Operations Intern", "Consulting Analyst", "Marketing Intern"],
      },
      {
        fieldId: "resumeInput",
        title: "Business path: impact evidence",
        prompt: "List cases, campaigns, analysis, user research, revenue/cost metrics, leadership, or cross-team work.",
        placeholder: "Case competition: analyzed market size...\nCampus project: improved signup conversion...\nClub: managed 300-person event...",
        presets: ["Data analysis", "Growth metric", "User research", "Leadership", "Case competition"],
      },
      {
        fieldId: "jdInput",
        title: "Business path: role criteria",
        prompt: "Paste the JD or list what the company values: analysis, execution, communication, ownership, industry interest.",
        placeholder: "Requires structured thinking, Excel/SQL, user insight, project management, communication...",
        presets: ["Structured thinking", "Data tools", "Execution", "Communication"],
      },
    ],
    design: [
      {
        fieldId: "roleInput",
        title: "Design path: creative target",
        prompt: "Which creative role are you targeting? Add medium if useful.",
        placeholder: "UI/UX Designer Intern / Brand Designer / Content Operations Intern",
        presets: ["UX Designer", "Visual Designer", "Content Intern", "Brand Designer"],
      },
      {
        fieldId: "resumeInput",
        title: "Design path: portfolio story",
        prompt: "List portfolio pieces, users, constraints, design decisions, tools, audience response, and links.",
        placeholder: "Portfolio: redesigned campus app flow for freshmen...\nTools: Figma, PS...\nResult: improved task completion...",
        presets: ["Portfolio link", "User problem", "Design decision", "Tool stack", "Audience result"],
      },
      {
        fieldId: "jdInput",
        title: "Design path: taste and requirements",
        prompt: "Paste the JD or describe required style, tools, portfolio expectations, and collaboration context.",
        placeholder: "Requires Figma, user research, visual system, portfolio, product collaboration...",
        presets: ["Portfolio required", "Figma", "User research", "Visual system"],
      },
    ],
    humanities: [
      {
        fieldId: "roleInput",
        title: "Humanities path: target scene",
        prompt: "Which role scene are you aiming for: content, research, public affairs, HR, editing, or operations?",
        placeholder: "Content Strategy Intern / Research Assistant / HR Intern",
        presets: ["Content Intern", "Research Assistant", "HR Intern", "Public Affairs"],
      },
      {
        fieldId: "resumeInput",
        title: "Humanities path: transferable evidence",
        prompt: "List writing, research, interviews, events, policy analysis, languages, community work, or publications.",
        placeholder: "Research: interviewed 20 participants...\nWriting: published articles...\nEvent: coordinated a forum...",
        presets: ["Writing sample", "Research method", "Interview", "Event planning", "Language skill"],
      },
      {
        fieldId: "jdInput",
        title: "Humanities path: employer language",
        prompt: "Paste the JD or list required communication, research, stakeholder, writing, and organization signals.",
        placeholder: "Requires strong writing, research, stakeholder communication, project coordination...",
        presets: ["Writing", "Research", "Stakeholder communication", "Coordination"],
      },
    ],
    education: [
      {
        fieldId: "roleInput",
        title: "Education path: service role",
        prompt: "Which learner or community are you trying to serve?",
        placeholder: "Teaching Assistant / Education Operations Intern / NGO Program Intern",
        presets: ["Teaching Assistant", "Education Ops", "NGO Program", "Student Mentor"],
      },
      {
        fieldId: "resumeInput",
        title: "Education path: service impact",
        prompt: "List tutoring, curriculum, mentoring, volunteer service, program operations, audience size, and outcomes.",
        placeholder: "Tutored 12 students...\nDesigned workshop materials...\nOperated volunteer program for 80 participants...",
        presets: ["Teaching", "Curriculum", "Mentoring", "Volunteer program", "Learner outcome"],
      },
      {
        fieldId: "jdInput",
        title: "Education path: trust signals",
        prompt: "Paste the JD or list required empathy, communication, operations, curriculum, and responsibility signals.",
        placeholder: "Requires patience, teaching ability, communication, program execution, student support...",
        presets: ["Teaching ability", "Empathy", "Program execution", "Student support"],
      },
    ],
    research: [
      {
        fieldId: "roleInput",
        title: "Research path: academic target",
        prompt: "Are you targeting research assistant, lab intern, graduate application, or academic CV direction?",
        placeholder: "Research Assistant / Lab Intern / Graduate Application",
        presets: ["Research Assistant", "Lab Intern", "Graduate Application", "Academic CV"],
      },
      {
        fieldId: "resumeInput",
        title: "Research path: methods and output",
        prompt: "List research questions, methods, lab tools, datasets, papers, posters, advisor projects, and findings.",
        placeholder: "Research: built dataset, ran regression/experiments...\nPaper: co-authored poster...\nTools: Python, SPSS, lab equipment...",
        presets: ["Research question", "Method", "Dataset", "Paper/poster", "Advisor project"],
      },
      {
        fieldId: "jdInput",
        title: "Research path: evaluation criteria",
        prompt: "Paste the requirement or describe expected methods, domain knowledge, tools, writing, and rigor.",
        placeholder: "Requires literature review, experiment design, Python/R, academic writing, attention to detail...",
        presets: ["Methods", "Tools", "Academic writing", "Domain knowledge"],
      },
    ],
  },
  "zh-CN": {
    engineering: [
      {
        fieldId: "roleInput",
        title: "\u5de5\u79d1\u8def\u7ebf\uff1a\u9501\u5b9a\u6280\u672f\u5c97",
        prompt: "\u4f60\u8981\u6295\u54ea\u7c7b\u6280\u672f\u5c97\uff1f\u5982\u679c\u77e5\u9053\u6280\u672f\u6808\uff0c\u4e5f\u4e00\u8d77\u5199\u4e0a\u3002",
        placeholder: "\u540e\u7aef\u5f00\u53d1\u5b9e\u4e60\u751f / \u5d4c\u5165\u5f0f\u5b9e\u4e60\u751f / AI \u5de5\u7a0b\u5e08",
        presets: ["\u540e\u7aef\u5f00\u53d1", "\u524d\u7aef\u5f00\u53d1", "AI \u5de5\u7a0b", "\u5d4c\u5165\u5f0f"],
      },
      {
        fieldId: "resumeInput",
        title: "\u5de5\u79d1\u8def\u7ebf\uff1a\u8bc1\u660e\u4f60\u771f\u505a\u8fc7",
        prompt: "\u5199\u9879\u76ee\u3001\u7cfb\u7edf\u3001\u7b97\u6cd5\u3001\u5b9e\u9a8c\u3001\u5de5\u5177\u3001\u89c4\u6a21\u3001\u4fee\u8fc7\u7684 bug \u548c\u91cf\u5316\u7ed3\u679c\u3002",
        placeholder: "\u9879\u76ee\uff1a\u7528 FastAPI \u505a\u670d\u52a1\uff0c\u8bbe\u8ba1\u6570\u636e\u8868\uff0c\u652f\u6301 300 \u4eba\u4f7f\u7528...\n\u8bfe\u7a0b\uff1a\u64cd\u4f5c\u7cfb\u7edf\u3001\u6570\u636e\u5e93\u3001\u8ba1\u7f51...\n\u6bd4\u8d5b\uff1a\u7b97\u6cd5\u8bad\u7ec3...",
        presets: ["\u9879\u76ee + \u6280\u672f\u6808", "\u7cfb\u7edf\u8bbe\u8ba1", "\u6838\u5fc3\u8bfe\u7a0b", "\u7b97\u6cd5\u6bd4\u8d5b", "GitHub"],
      },
      {
        fieldId: "jdInput",
        title: "\u5de5\u79d1\u8def\u7ebf\uff1a\u62c6\u89e3\u62db\u8058\u4fe1\u53f7",
        prompt: "\u7c98\u8d34 JD\uff0c\u6216\u5199\u4e0b\u6280\u672f\u6808\u3001\u5de5\u7a0b\u4e60\u60ef\u3001\u534f\u4f5c\u8981\u6c42\u548c\u5173\u952e\u8bcd\u3002",
        placeholder: "\u8981\u6c42 Python/Java\uff0c\u6570\u636e\u5e93\uff0c\u5206\u5e03\u5f0f\uff0c\u6392\u969c\uff0c\u4e3b\u52a8\u6027\uff0c\u6c9f\u901a...",
        presets: ["\u6280\u672f\u6808", "\u7cfb\u7edf\u7a33\u5b9a\u6027", "\u56e2\u961f\u534f\u4f5c", "\u95ee\u9898\u89e3\u51b3"],
      },
    ],
    business: [
      {
        fieldId: "roleInput",
        title: "\u5546\u79d1\u8def\u7ebf\uff1a\u9009\u62e9\u804c\u80fd",
        prompt: "\u4f60\u60f3\u6295\u4ea7\u54c1\u3001\u8fd0\u8425\u3001\u54a8\u8be2\u3001\u5e02\u573a\u3001\u91d1\u878d\u8fd8\u662f\u6218\u7565\uff1f",
        placeholder: "\u4ea7\u54c1\u7ecf\u7406\u5b9e\u4e60\u751f / \u8fd0\u8425\u5b9e\u4e60\u751f / \u6218\u7565\u5206\u6790",
        presets: ["\u4ea7\u54c1\u5b9e\u4e60", "\u8fd0\u8425\u5b9e\u4e60", "\u54a8\u8be2\u5206\u6790", "\u5e02\u573a\u5b9e\u4e60"],
      },
      {
        fieldId: "resumeInput",
        title: "\u5546\u79d1\u8def\u7ebf\uff1a\u627e\u5f71\u54cd\u529b\u8bc1\u636e",
        prompt: "\u5199\u6848\u4f8b\u3001\u6d3b\u52a8\u3001\u5206\u6790\u3001\u7528\u7814\u3001\u6536\u5165/\u6210\u672c\u6307\u6807\u3001\u7ec4\u7ec7\u534f\u4f5c\u6216\u9886\u5bfc\u529b\u3002",
        placeholder: "\u6848\u4f8b\u6bd4\u8d5b\uff1a\u5206\u6790\u5e02\u573a\u89c4\u6a21...\n\u6821\u56ed\u9879\u76ee\uff1a\u63d0\u5347\u62a5\u540d\u8f6c\u5316...\n\u793e\u56e2\uff1a\u7ba1\u7406 300 \u4eba\u6d3b\u52a8...",
        presets: ["\u6570\u636e\u5206\u6790", "\u589e\u957f\u6307\u6807", "\u7528\u6237\u7814\u7a76", "\u9886\u5bfc\u529b", "\u6848\u4f8b\u6bd4\u8d5b"],
      },
      {
        fieldId: "jdInput",
        title: "\u5546\u79d1\u8def\u7ebf\uff1a\u5bf9\u9f50\u4f01\u4e1a\u8bed\u8a00",
        prompt: "\u7c98\u8d34 JD\uff0c\u6216\u5199\u4f01\u4e1a\u770b\u91cd\u7684\u5206\u6790\u3001\u6267\u884c\u3001\u6c9f\u901a\u3001\u4e3b\u52a8\u6027\u548c\u884c\u4e1a\u5174\u8da3\u3002",
        placeholder: "\u8981\u6c42\u7ed3\u6784\u5316\u601d\u7ef4\uff0cExcel/SQL\uff0c\u7528\u6237\u6d1e\u5bdf\uff0c\u9879\u76ee\u7ba1\u7406\uff0c\u6c9f\u901a...",
        presets: ["\u7ed3\u6784\u5316\u601d\u7ef4", "\u6570\u636e\u5de5\u5177", "\u6267\u884c\u529b", "\u6c9f\u901a"],
      },
    ],
  },
};

Object.assign(disciplineQuestSteps["zh-CN"], {
  design: [
    {
      fieldId: "roleInput",
      title: "\u8bbe\u8ba1\u4f20\u5a92\u8def\u7ebf\uff1a\u786e\u5b9a\u521b\u610f\u5c97\u4f4d",
      prompt: "\u4f60\u8981\u6295 UI/UX\u3001\u89c6\u89c9\u3001\u54c1\u724c\u3001\u5185\u5bb9\u8fd0\u8425\u8fd8\u662f\u4f20\u5a92\u7c7b\u5c97\u4f4d\uff1f",
      placeholder: "UI/UX \u8bbe\u8ba1\u5b9e\u4e60\u751f / \u54c1\u724c\u8bbe\u8ba1 / \u5185\u5bb9\u8fd0\u8425",
      presets: ["UX \u8bbe\u8ba1", "\u89c6\u89c9\u8bbe\u8ba1", "\u5185\u5bb9\u8fd0\u8425", "\u54c1\u724c\u8bbe\u8ba1"],
    },
    {
      fieldId: "resumeInput",
      title: "\u8bbe\u8ba1\u4f20\u5a92\u8def\u7ebf\uff1a\u8bb2\u6e05\u4f5c\u54c1\u6545\u4e8b",
      prompt: "\u5199\u4f5c\u54c1\u96c6\u3001\u7528\u6237/\u53d7\u4f17\u3001\u8bbe\u8ba1\u76ee\u6807\u3001\u89e3\u51b3\u65b9\u6848\u3001\u5de5\u5177\u3001\u6570\u636e\u53cd\u9988\u548c\u94fe\u63a5\u3002",
      placeholder: "\u4f5c\u54c1\uff1a\u91cd\u8bbe\u6821\u56ed App \u6d41\u7a0b...\n\u5de5\u5177\uff1aFigma/PS/AI...\n\u7ed3\u679c\uff1a\u63d0\u5347\u4efb\u52a1\u5b8c\u6210\u7387...",
      presets: ["\u4f5c\u54c1\u96c6\u94fe\u63a5", "\u7528\u6237\u95ee\u9898", "\u8bbe\u8ba1\u51b3\u7b56", "\u5de5\u5177\u6808", "\u53d7\u4f17\u53cd\u9988"],
    },
    {
      fieldId: "jdInput",
      title: "\u8bbe\u8ba1\u4f20\u5a92\u8def\u7ebf\uff1a\u5339\u914d\u5ba1\u7f8e\u548c\u8981\u6c42",
      prompt: "\u7c98\u8d34 JD\uff0c\u6216\u5199\u5de5\u5177\u3001\u4f5c\u54c1\u96c6\u8981\u6c42\u3001\u98ce\u683c\u3001\u7528\u7814\u548c\u534f\u4f5c\u573a\u666f\u3002",
      placeholder: "\u8981\u6c42 Figma\uff0c\u7528\u6237\u7814\u7a76\uff0c\u89c6\u89c9\u7cfb\u7edf\uff0c\u4f5c\u54c1\u96c6\uff0c\u4ea7\u54c1\u534f\u4f5c...",
      presets: ["\u4f5c\u54c1\u96c6", "Figma", "\u7528\u7814", "\u89c6\u89c9\u7cfb\u7edf"],
    },
  ],
  humanities: [
    {
      fieldId: "roleInput",
      title: "\u4eba\u6587\u793e\u79d1\u8def\u7ebf\uff1a\u9009\u62e9\u5e94\u7528\u573a\u666f",
      prompt: "\u4f60\u60f3\u6295\u5185\u5bb9\u3001\u7814\u7a76\u3001\u516c\u5171\u4e8b\u52a1\u3001HR\u3001\u7f16\u8f91\u8fd8\u662f\u8fd0\u8425\uff1f",
      placeholder: "\u5185\u5bb9\u7b56\u7565\u5b9e\u4e60\u751f / \u7814\u7a76\u52a9\u7406 / HR \u5b9e\u4e60\u751f",
      presets: ["\u5185\u5bb9\u5b9e\u4e60", "\u7814\u7a76\u52a9\u7406", "HR \u5b9e\u4e60", "\u516c\u5171\u4e8b\u52a1"],
    },
    {
      fieldId: "resumeInput",
      title: "\u4eba\u6587\u793e\u79d1\u8def\u7ebf\uff1a\u63d0\u70bc\u53ef\u8fc1\u79fb\u80fd\u529b",
      prompt: "\u5199\u5199\u4f5c\u3001\u8c03\u7814\u3001\u8bbf\u8c08\u3001\u6d3b\u52a8\u3001\u653f\u7b56\u5206\u6790\u3001\u5916\u8bed\u3001\u793e\u7fa4\u548c\u53d1\u8868\u3002",
      placeholder: "\u7814\u7a76\uff1a\u8bbf\u8c08 20 \u4f4d\u53d7\u8bbf\u8005...\n\u5199\u4f5c\uff1a\u53d1\u8868\u6587\u7ae0...\n\u6d3b\u52a8\uff1a\u534f\u8c03\u8bba\u575b...",
      presets: ["\u5199\u4f5c\u6837\u672c", "\u7814\u7a76\u65b9\u6cd5", "\u8bbf\u8c08", "\u6d3b\u52a8\u7b56\u5212", "\u8bed\u8a00\u80fd\u529b"],
    },
    {
      fieldId: "jdInput",
      title: "\u4eba\u6587\u793e\u79d1\u8def\u7ebf\uff1a\u5bf9\u9f50\u96c7\u4e3b\u8bed\u8a00",
      prompt: "\u7c98\u8d34 JD\uff0c\u6216\u5199\u5bf9\u5199\u4f5c\u3001\u7814\u7a76\u3001\u6c9f\u901a\u3001\u7ec4\u7ec7\u548c\u5229\u76ca\u76f8\u5173\u65b9\u7684\u8981\u6c42\u3002",
      placeholder: "\u8981\u6c42\u5199\u4f5c\u80fd\u529b\uff0c\u7814\u7a76\u80fd\u529b\uff0c\u6c9f\u901a\uff0c\u9879\u76ee\u534f\u8c03...",
      presets: ["\u5199\u4f5c", "\u7814\u7a76", "\u6c9f\u901a", "\u534f\u8c03"],
    },
  ],
  education: [
    {
      fieldId: "roleInput",
      title: "\u6559\u80b2\u516c\u76ca\u8def\u7ebf\uff1a\u786e\u5b9a\u670d\u52a1\u5bf9\u8c61",
      prompt: "\u4f60\u60f3\u505a\u52a9\u6559\u3001\u8bfe\u7a0b\u8fd0\u8425\u3001\u516c\u76ca\u9879\u76ee\u8fd8\u662f\u5b66\u751f\u652f\u6301\uff1f",
      placeholder: "\u52a9\u6559 / \u6559\u80b2\u8fd0\u8425\u5b9e\u4e60\u751f / NGO \u9879\u76ee\u5b9e\u4e60\u751f",
      presets: ["\u52a9\u6559", "\u6559\u80b2\u8fd0\u8425", "\u516c\u76ca\u9879\u76ee", "\u5b66\u751f\u5bfc\u5e08"],
    },
    {
      fieldId: "resumeInput",
      title: "\u6559\u80b2\u516c\u76ca\u8def\u7ebf\uff1a\u8bc1\u660e\u670d\u52a1\u5f71\u54cd",
      prompt: "\u5199\u8f85\u5bfc\u3001\u8bfe\u7a0b\u8bbe\u8ba1\u3001\u966a\u4f34\u3001\u5fd7\u613f\u670d\u52a1\u3001\u9879\u76ee\u8fd0\u8425\u3001\u4eba\u6570\u548c\u6539\u53d8\u3002",
      placeholder: "\u8f85\u5bfc 12 \u540d\u5b66\u751f...\n\u8bbe\u8ba1\u5de5\u4f5c\u574a\u6750\u6599...\n\u8fd0\u8425 80 \u4eba\u5fd7\u613f\u9879\u76ee...",
      presets: ["\u6559\u5b66", "\u8bfe\u7a0b", "\u966a\u4f34", "\u5fd7\u613f\u9879\u76ee", "\u5b66\u4e60\u6210\u679c"],
    },
    {
      fieldId: "jdInput",
      title: "\u6559\u80b2\u516c\u76ca\u8def\u7ebf\uff1a\u8865\u8db3\u4fe1\u4efb\u4fe1\u53f7",
      prompt: "\u7c98\u8d34 JD\uff0c\u6216\u5199\u540c\u7406\u5fc3\u3001\u6c9f\u901a\u3001\u6267\u884c\u3001\u8bfe\u7a0b\u548c\u8d23\u4efb\u611f\u8981\u6c42\u3002",
      placeholder: "\u8981\u6c42\u8010\u5fc3\uff0c\u6559\u5b66\u80fd\u529b\uff0c\u6c9f\u901a\uff0c\u9879\u76ee\u6267\u884c\uff0c\u5b66\u751f\u652f\u6301...",
      presets: ["\u6559\u5b66\u80fd\u529b", "\u540c\u7406\u5fc3", "\u9879\u76ee\u6267\u884c", "\u5b66\u751f\u652f\u6301"],
    },
  ],
  research: [
    {
      fieldId: "roleInput",
      title: "\u79d1\u7814\u5347\u5b66\u8def\u7ebf\uff1a\u786e\u5b9a\u5b66\u672f\u76ee\u6807",
      prompt: "\u4f60\u8981\u6295\u79d1\u7814\u52a9\u7406\u3001\u5b9e\u9a8c\u5ba4\u5b9e\u4e60\u3001\u7814\u7a76\u751f\u7533\u8bf7\u8fd8\u662f\u5b66\u672f CV\uff1f",
      placeholder: "\u79d1\u7814\u52a9\u7406 / \u5b9e\u9a8c\u5ba4\u5b9e\u4e60 / \u7814\u7a76\u751f\u7533\u8bf7",
      presets: ["\u79d1\u7814\u52a9\u7406", "\u5b9e\u9a8c\u5ba4\u5b9e\u4e60", "\u7814\u7a76\u751f\u7533\u8bf7", "\u5b66\u672f CV"],
    },
    {
      fieldId: "resumeInput",
      title: "\u79d1\u7814\u5347\u5b66\u8def\u7ebf\uff1a\u5199\u65b9\u6cd5\u548c\u4ea7\u51fa",
      prompt: "\u5199\u7814\u7a76\u95ee\u9898\u3001\u65b9\u6cd5\u3001\u5b9e\u9a8c/\u6570\u636e\u3001\u8bba\u6587\u3001\u6d77\u62a5\u3001\u5bfc\u5e08\u9879\u76ee\u548c\u53d1\u73b0\u3002",
      placeholder: "\u7814\u7a76\uff1a\u6784\u5efa\u6570\u636e\u96c6\uff0c\u8dd1\u56de\u5f52/\u5b9e\u9a8c...\n\u8bba\u6587\uff1a\u53c2\u4e0e\u6d77\u62a5...\n\u5de5\u5177\uff1aPython/SPSS/\u5b9e\u9a8c\u4eea\u5668...",
      presets: ["\u7814\u7a76\u95ee\u9898", "\u65b9\u6cd5", "\u6570\u636e\u96c6", "\u8bba\u6587/\u6d77\u62a5", "\u5bfc\u5e08\u9879\u76ee"],
    },
    {
      fieldId: "jdInput",
      title: "\u79d1\u7814\u5347\u5b66\u8def\u7ebf\uff1a\u5bf9\u9f50\u8bc4\u4f30\u6807\u51c6",
      prompt: "\u7c98\u8d34\u8981\u6c42\uff0c\u6216\u5199\u65b9\u6cd5\u3001\u9886\u57df\u77e5\u8bc6\u3001\u5de5\u5177\u3001\u5199\u4f5c\u548c\u4e25\u8c28\u6027\u3002",
      placeholder: "\u8981\u6c42\u6587\u732e\u7efc\u8ff0\uff0c\u5b9e\u9a8c\u8bbe\u8ba1\uff0cPython/R\uff0c\u5b66\u672f\u5199\u4f5c\uff0c\u7ec6\u81f4...",
      presets: ["\u65b9\u6cd5", "\u5de5\u5177", "\u5b66\u672f\u5199\u4f5c", "\u9886\u57df\u77e5\u8bc6"],
    },
  ],
});

let questIndex = 0;
const questState = {
  role: "",
  jd: "",
  modules: {},
};

const moduleCopy = {
  en: {
    engineering: {
      evidenceTitle: "Engineering proof",
      evidenceQuestion: "Describe one project, system, experiment, or technical problem you actually built or fixed.",
      evidencePlaceholder: "Project: built a campus service with FastAPI, designed database tables, supported 300+ users...",
      evidencePresets: ["Project + stack", "System design", "Debugging story", "GitHub link"],
      skillTitle: "Technical signal",
      skillQuestion: "List your stack, courses, tools, algorithms, engineering habits, and measurable outcomes.",
      skillPlaceholder: "Python, Java, databases, operating systems, networks, testing, deployment...",
      skillPresets: ["Tech stack", "Core courses", "Tools", "Metrics"],
    },
    business: {
      evidenceTitle: "Business impact",
      evidenceQuestion: "Describe one case, campaign, analysis, product, operation, or leadership moment with impact.",
      evidencePlaceholder: "Case competition: sized the market and proposed a go-to-market plan...",
      evidencePresets: ["Case", "User research", "Operations", "Leadership"],
      skillTitle: "Execution signal",
      skillQuestion: "List tools, methods, metrics, stakeholder work, and business judgement signals.",
      skillPlaceholder: "Excel, SQL, research, growth metrics, project management, presentation...",
      skillPresets: ["Data tools", "Metrics", "Communication", "Execution"],
    },
    design: {
      evidenceTitle: "Portfolio story",
      evidenceQuestion: "Describe one portfolio piece: user, constraint, design decision, result, and link if any.",
      evidencePlaceholder: "Portfolio: redesigned a campus app flow for freshmen; used Figma; improved task completion...",
      evidencePresets: ["Portfolio link", "User problem", "Design decision", "Result"],
      skillTitle: "Creative signal",
      skillQuestion: "List tools, visual style, research methods, collaboration, and audience feedback.",
      skillPlaceholder: "Figma, PS, AI, user interviews, design systems, brand work...",
      skillPresets: ["Figma", "User research", "Visual system", "Audience feedback"],
    },
    humanities: {
      evidenceTitle: "Transferable evidence",
      evidenceQuestion: "Describe one writing, research, interview, public affairs, editing, or community project.",
      evidencePlaceholder: "Research: interviewed 20 participants and summarized findings into a report...",
      evidencePresets: ["Writing", "Research", "Interview", "Event"],
      skillTitle: "Communication signal",
      skillQuestion: "List writing, research, languages, coordination, stakeholder, and analysis strengths.",
      skillPlaceholder: "Writing, desk research, interviews, event coordination, English, policy analysis...",
      skillPresets: ["Writing", "Research", "Language", "Coordination"],
    },
    education: {
      evidenceTitle: "Service impact",
      evidenceQuestion: "Describe one teaching, tutoring, curriculum, volunteer, or student-support experience.",
      evidencePlaceholder: "Tutored 12 students; designed weekly materials; improved participation...",
      evidencePresets: ["Teaching", "Mentoring", "Curriculum", "Volunteer"],
      skillTitle: "Trust signal",
      skillQuestion: "List empathy, communication, execution, curriculum, operations, and responsibility evidence.",
      skillPlaceholder: "Teaching, patience, program operations, workshop design, student support...",
      skillPresets: ["Empathy", "Teaching", "Execution", "Student support"],
    },
    research: {
      evidenceTitle: "Research output",
      evidenceQuestion: "Describe one research question, method, dataset, experiment, paper, poster, or lab project.",
      evidencePlaceholder: "Research: built a dataset, ran regression/experiments, summarized findings...",
      evidencePresets: ["Research question", "Method", "Dataset", "Paper/poster"],
      skillTitle: "Academic signal",
      skillQuestion: "List methods, tools, domain knowledge, writing, rigor, and advisor/lab context.",
      skillPlaceholder: "Literature review, Python/R, SPSS, experiment design, academic writing...",
      skillPresets: ["Methods", "Tools", "Academic writing", "Domain knowledge"],
    },
  },
  "zh-CN": {
    engineering: {
      evidenceTitle: "\u5de5\u7a0b\u8bc1\u636e",
      evidenceQuestion: "\u5199\u4e00\u4e2a\u4f60\u771f\u505a\u8fc7\u7684\u9879\u76ee\u3001\u7cfb\u7edf\u3001\u5b9e\u9a8c\u6216\u6280\u672f\u95ee\u9898\uff1a\u7528\u4e86\u4ec0\u4e48\uff0c\u89e3\u51b3\u4e86\u4ec0\u4e48\uff0c\u7ed3\u679c\u600e\u6837\u3002",
      evidencePlaceholder: "\u9879\u76ee\uff1a\u7528 FastAPI \u505a\u6821\u56ed\u670d\u52a1\uff0c\u8bbe\u8ba1\u6570\u636e\u8868\uff0c\u652f\u6301 300+ \u5b66\u751f\u62a5\u540d...",
      evidencePresets: ["\u9879\u76ee + \u6280\u672f\u6808", "\u7cfb\u7edf\u8bbe\u8ba1", "\u6392\u969c\u6545\u4e8b", "GitHub"],
      skillTitle: "\u6280\u672f\u4fe1\u53f7",
      skillQuestion: "\u5199\u6280\u672f\u6808\u3001\u6838\u5fc3\u8bfe\u7a0b\u3001\u5de5\u5177\u3001\u7b97\u6cd5\u3001\u5de5\u7a0b\u4e60\u60ef\u548c\u91cf\u5316\u7ed3\u679c\u3002",
      skillPlaceholder: "Python / Java / \u6570\u636e\u5e93 / \u64cd\u4f5c\u7cfb\u7edf / \u8ba1\u7b97\u673a\u7f51\u7edc / \u6d4b\u8bd5 / \u90e8\u7f72...",
      skillPresets: ["\u6280\u672f\u6808", "\u6838\u5fc3\u8bfe\u7a0b", "\u5de5\u5177", "\u91cf\u5316\u7ed3\u679c"],
    },
    business: {
      evidenceTitle: "\u5546\u4e1a\u5f71\u54cd",
      evidenceQuestion: "\u5199\u4e00\u4e2a\u6848\u4f8b\u3001\u6d3b\u52a8\u3001\u5206\u6790\u3001\u4ea7\u54c1\u3001\u8fd0\u8425\u6216\u9886\u5bfc\u529b\u6545\u4e8b\uff0c\u5c3d\u91cf\u5e26\u6570\u636e\u3002",
      evidencePlaceholder: "\u6848\u4f8b\u6bd4\u8d5b\uff1a\u5206\u6790\u5e02\u573a\u89c4\u6a21\uff0c\u8bbe\u8ba1\u589e\u957f\u65b9\u6848...",
      evidencePresets: ["\u6848\u4f8b", "\u7528\u7814", "\u8fd0\u8425", "\u9886\u5bfc\u529b"],
      skillTitle: "\u6267\u884c\u4fe1\u53f7",
      skillQuestion: "\u5199\u5de5\u5177\u3001\u65b9\u6cd5\u3001\u6307\u6807\u3001\u534f\u4f5c\u3001\u5546\u4e1a\u5224\u65ad\u548c\u63a8\u8fdb\u80fd\u529b\u3002",
      skillPlaceholder: "Excel / SQL / \u7528\u6237\u7814\u7a76 / \u589e\u957f\u6307\u6807 / \u9879\u76ee\u7ba1\u7406 / \u6c47\u62a5...",
      skillPresets: ["\u6570\u636e\u5de5\u5177", "\u6307\u6807", "\u6c9f\u901a", "\u6267\u884c"],
    },
    design: {
      evidenceTitle: "\u4f5c\u54c1\u6545\u4e8b",
      evidenceQuestion: "\u5199\u4e00\u4e2a\u4f5c\u54c1\uff1a\u7528\u6237\u662f\u8c01\uff0c\u7ea6\u675f\u662f\u4ec0\u4e48\uff0c\u4f60\u505a\u4e86\u54ea\u4e2a\u8bbe\u8ba1\u51b3\u7b56\uff0c\u7ed3\u679c\u600e\u6837\u3002",
      evidencePlaceholder: "\u4f5c\u54c1\uff1a\u91cd\u8bbe\u6821\u56ed App \u65b0\u751f\u6d41\u7a0b\uff0c\u7528 Figma \u5b8c\u6210\u539f\u578b...",
      evidencePresets: ["\u4f5c\u54c1\u96c6", "\u7528\u6237\u95ee\u9898", "\u8bbe\u8ba1\u51b3\u7b56", "\u7ed3\u679c"],
      skillTitle: "\u521b\u610f\u4fe1\u53f7",
      skillQuestion: "\u5199\u5de5\u5177\u3001\u98ce\u683c\u3001\u7528\u7814\u65b9\u6cd5\u3001\u534f\u4f5c\u65b9\u5f0f\u548c\u53d7\u4f17\u53cd\u9988\u3002",
      skillPlaceholder: "Figma / PS / AI / \u7528\u6237\u8bbf\u8c08 / \u8bbe\u8ba1\u7cfb\u7edf / \u54c1\u724c...",
      skillPresets: ["Figma", "\u7528\u7814", "\u89c6\u89c9\u7cfb\u7edf", "\u53cd\u9988"],
    },
    humanities: {
      evidenceTitle: "\u8fc1\u79fb\u8bc1\u636e",
      evidenceQuestion: "\u5199\u4e00\u4e2a\u5199\u4f5c\u3001\u8c03\u7814\u3001\u8bbf\u8c08\u3001\u516c\u5171\u4e8b\u52a1\u3001\u7f16\u8f91\u6216\u793e\u7fa4\u9879\u76ee\u3002",
      evidencePlaceholder: "\u8c03\u7814\uff1a\u8bbf\u8c08 20 \u4f4d\u53d7\u8bbf\u8005\uff0c\u6574\u7406\u6210\u7814\u7a76\u62a5\u544a...",
      evidencePresets: ["\u5199\u4f5c", "\u8c03\u7814", "\u8bbf\u8c08", "\u6d3b\u52a8"],
      skillTitle: "\u6c9f\u901a\u4fe1\u53f7",
      skillQuestion: "\u5199\u5199\u4f5c\u3001\u7814\u7a76\u3001\u5916\u8bed\u3001\u7ec4\u7ec7\u534f\u8c03\u3001\u5229\u76ca\u76f8\u5173\u65b9\u548c\u5206\u6790\u80fd\u529b\u3002",
      skillPlaceholder: "\u5199\u4f5c / \u684c\u9762\u7814\u7a76 / \u8bbf\u8c08 / \u6d3b\u52a8\u534f\u8c03 / \u82f1\u8bed / \u653f\u7b56\u5206\u6790...",
      skillPresets: ["\u5199\u4f5c", "\u7814\u7a76", "\u8bed\u8a00", "\u534f\u8c03"],
    },
    education: {
      evidenceTitle: "\u670d\u52a1\u5f71\u54cd",
      evidenceQuestion: "\u5199\u4e00\u4e2a\u6559\u5b66\u3001\u8f85\u5bfc\u3001\u8bfe\u7a0b\u8bbe\u8ba1\u3001\u5fd7\u613f\u670d\u52a1\u6216\u5b66\u751f\u652f\u6301\u7ecf\u5386\u3002",
      evidencePlaceholder: "\u8f85\u5bfc 12 \u540d\u5b66\u751f\uff0c\u8bbe\u8ba1\u6bcf\u5468\u6750\u6599\uff0c\u63d0\u5347\u53c2\u4e0e\u5ea6...",
      evidencePresets: ["\u6559\u5b66", "\u966a\u4f34", "\u8bfe\u7a0b", "\u5fd7\u613f"],
      skillTitle: "\u4fe1\u4efb\u4fe1\u53f7",
      skillQuestion: "\u5199\u540c\u7406\u5fc3\u3001\u6c9f\u901a\u3001\u6267\u884c\u3001\u8bfe\u7a0b\u3001\u8fd0\u8425\u548c\u8d23\u4efb\u611f\u8bc1\u636e\u3002",
      skillPlaceholder: "\u6559\u5b66 / \u8010\u5fc3 / \u9879\u76ee\u8fd0\u8425 / \u5de5\u4f5c\u574a\u8bbe\u8ba1 / \u5b66\u751f\u652f\u6301...",
      skillPresets: ["\u540c\u7406\u5fc3", "\u6559\u5b66", "\u6267\u884c", "\u5b66\u751f\u652f\u6301"],
    },
    research: {
      evidenceTitle: "\u79d1\u7814\u4ea7\u51fa",
      evidenceQuestion: "\u5199\u4e00\u4e2a\u7814\u7a76\u95ee\u9898\u3001\u65b9\u6cd5\u3001\u6570\u636e\u96c6\u3001\u5b9e\u9a8c\u3001\u8bba\u6587\u3001\u6d77\u62a5\u6216\u5b9e\u9a8c\u5ba4\u9879\u76ee\u3002",
      evidencePlaceholder: "\u7814\u7a76\uff1a\u6784\u5efa\u6570\u636e\u96c6\uff0c\u8dd1\u56de\u5f52/\u5b9e\u9a8c\uff0c\u603b\u7ed3\u53d1\u73b0...",
      evidencePresets: ["\u7814\u7a76\u95ee\u9898", "\u65b9\u6cd5", "\u6570\u636e\u96c6", "\u8bba\u6587/\u6d77\u62a5"],
      skillTitle: "\u5b66\u672f\u4fe1\u53f7",
      skillQuestion: "\u5199\u65b9\u6cd5\u3001\u5de5\u5177\u3001\u9886\u57df\u77e5\u8bc6\u3001\u5199\u4f5c\u3001\u4e25\u8c28\u6027\u548c\u5bfc\u5e08/\u5b9e\u9a8c\u5ba4\u80cc\u666f\u3002",
      skillPlaceholder: "\u6587\u732e\u7efc\u8ff0 / Python / R / SPSS / \u5b9e\u9a8c\u8bbe\u8ba1 / \u5b66\u672f\u5199\u4f5c...",
      skillPresets: ["\u65b9\u6cd5", "\u5de5\u5177", "\u5b66\u672f\u5199\u4f5c", "\u9886\u57df\u77e5\u8bc6"],
    },
  },
};

function getDisciplineCopy() {
  const locale = currentLocale();
  const discipline = questDisciplineSelect?.value || "engineering";
  return moduleCopy[locale]?.[discipline] || moduleCopy.en[discipline] || moduleCopy.en.engineering;
}

function getTemplateLabel() {
  if (!templateSelect) return "";
  return templateSelect.options[templateSelect.selectedIndex]?.textContent || templateSelect.value;
}

function currentTemplateName() {
  return templateSelect?.value || "fresh_graduate";
}

function templatePreviewNote(templateName) {
  const notes = {
    en: {
      fresh_graduate: "Education and projects first",
      tech_modern: "Stack and impact first",
      minimal: "Clean one-page scan",
      management: "Leadership and metrics first",
    },
    "zh-CN": {
      fresh_graduate: "\u6559\u80b2\u548c\u9879\u76ee\u4f18\u5148",
      tech_modern: "\u6280\u672f\u6808\u548c\u4ea7\u51fa\u4f18\u5148",
      minimal: "\u4e00\u9875\u6781\u7b80\u626b\u8bfb",
      management: "\u7ba1\u7406\u548c\u6307\u6807\u4f18\u5148",
    },
  };
  const locale = currentLocale();
  return notes[locale]?.[templateName] || notes.en[templateName] || "";
}

function splitProjectBlocks(value) {
  return value
    .split(/\n\s*\n+/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function renderPreviewBody(step, value) {
  if (!value) return `<span class="preview-empty">${t("previewEmpty")}</span>`;
  const isProjectStep = step.id === "evidence";
  const projectBlocks = isProjectStep ? splitProjectBlocks(value) : [];
  if (projectBlocks.length > 1) {
    return `<div class="preview-project-stack">${projectBlocks
      .map((item, index) => `<div class="preview-project"><b>${currentLocale() === "zh-CN" ? "\u9879\u76ee" : "Project"} ${index + 1}</b><p>${escapeHtml(item).replace(/\n/g, "<br>")}</p></div>`)
      .join("")}</div>`;
  }
  return escapeHtml(value).replace(/\n/g, "<br>");
}

function previewSectionTitle(step) {
  const title = step.title.replace(/^.*?\uff1a/, "").replace(/^Level \d+: /, "");
  const zhMap = {
    education: "\u6559\u80b2\u80cc\u666f",
    evidence: "\u9879\u76ee\u7ecf\u5386",
    skills: "\u6280\u80fd\u4e0e\u4f18\u52bf",
    jd: "\u76ee\u6807\u5c97\u4f4d",
  };
  const enMap = {
    education: "Education",
    evidence: "Projects",
    skills: "Skills",
    jd: "Target JD",
  };
  const map = currentLocale() === "zh-CN" ? zhMap : enMap;
  return map[step.id] || title;
}

function getModuleQuestSteps() {
  const locale = currentLocale();
  const copy = getDisciplineCopy();
  const isZh = locale === "zh-CN";
  return [
    {
      id: "target",
      target: "role",
      title: isZh ? "\u7b2c 1 \u5173\uff1a\u9501\u5b9a\u76ee\u6807" : "Level 1: Lock the target",
      prompt: isZh ? "\u4f60\u60f3\u7528\u8fd9\u4efd\u7b80\u5386\u6295\u4ec0\u4e48\u5c97\uff1f\u5199\u51c6\u5c97\u4f4d\u540d\uff0c\u6709\u516c\u53f8\u6216\u65b9\u5411\u4e5f\u5199\u4e0a\u3002" : "What role should this resume win? Add company type or direction if you know it.",
      placeholder: isZh ? "\u540e\u7aef\u5f00\u53d1\u5b9e\u4e60\u751f / AI \u4ea7\u54c1\u7ecf\u7406 / \u6570\u636e\u5206\u6790\u5b9e\u4e60\u751f" : "Backend Engineer Intern / AI Product Manager / Data Analyst Intern",
      presets: isZh ? ["\u540e\u7aef\u5f00\u53d1", "AI \u4ea7\u54c1", "\u6570\u636e\u5206\u6790", "\u6821\u62db"] : ["Backend", "AI Product", "Data Analyst", "Campus hire"],
    },
    {
      id: "education",
      target: "resume",
      title: isZh ? "\u7b2c 2 \u5173\uff1a\u5b66\u4e1a\u5e95\u76d8" : "Level 2: Academic base",
      prompt: isZh ? "\u5199\u5b66\u6821\u3001\u4e13\u4e1a\u3001\u5e74\u7ea7\u3001\u6838\u5fc3\u8bfe\u7a0b\u3001GPA/\u6392\u540d/\u5956\u5b66\u91d1\uff0c\u6ca1\u6709\u5c31\u7559\u7a7a\u3002" : "Add school, major, year, core courses, GPA/rank/scholarship if useful. Skip what you do not have.",
      placeholder: isZh ? "\u67d0\u5927\u5b66 / \u8ba1\u7b97\u673a\u79d1\u5b66 / 2026 \u5c4a / \u6570\u636e\u5e93\u3001\u64cd\u4f5c\u7cfb\u7edf..." : "University / Computer Science / Class of 2026 / Databases, OS...",
      presets: isZh ? ["\u5b66\u6821\u4e13\u4e1a", "\u6838\u5fc3\u8bfe\u7a0b", "\u5956\u5b66\u91d1", "\u6392\u540d"] : ["School + major", "Core courses", "Scholarship", "Rank"],
    },
    {
      id: "evidence",
      target: "resume",
      title: `${isZh ? "\u7b2c 3 \u5173\uff1a" : "Level 3: "}${copy.evidenceTitle}`,
      prompt: `${copy.evidenceQuestion}${isZh ? "\u5982\u679c\u6709\u591a\u4e2a\u9879\u76ee\uff0c\u7528\u7a7a\u884c\u5206\u9694\uff0c\u6211\u4f1a\u5728\u53f3\u4fa7\u5206\u6210\u591a\u5f20\u9879\u76ee\u5361\u3002" : " If you have multiple projects, separate them with a blank line and I will preview them as separate project cards."}`,
      placeholder: `${copy.evidencePlaceholder}${isZh ? "\n\n\u9879\u76ee 2\uff1a\u5199\u53e6\u4e00\u4e2a\u9879\u76ee..." : "\n\nProject 2: describe another project..."}`,
      presets: [...copy.evidencePresets, isZh ? "\u65b0\u589e\u4e00\u4e2a\u9879\u76ee" : "Add another project"],
    },
    {
      id: "skills",
      target: "resume",
      title: `${isZh ? "\u7b2c 4 \u5173\uff1a" : "Level 4: "}${copy.skillTitle}`,
      prompt: copy.skillQuestion,
      placeholder: copy.skillPlaceholder,
      presets: copy.skillPresets,
    },
    {
      id: "jd",
      target: "jd",
      title: isZh ? "\u7b2c 5 \u5173\uff1a\u5bf9\u9f50\u5c97\u4f4d" : "Level 5: Align the JD",
      prompt: isZh ? "\u7c98\u8d34 JD\uff0c\u6216\u8005\u7528\u5927\u767d\u8bdd\u5199\u4f01\u4e1a\u8981\u4ec0\u4e48\u3002\u6ca1 JD \u4e5f\u53ef\u5199\u76ee\u6807\u516c\u53f8\u548c\u5173\u952e\u8981\u6c42\u3002" : "Paste the JD, or describe what the employer wants. If you do not have one, write the target company and key signals.",
      placeholder: isZh ? "\u8981\u6c42\u719f\u6089 Python/Java\uff0c\u6570\u636e\u5e93\uff0c\u9879\u76ee\u7ecf\u5386\uff0c\u6c9f\u901a\u534f\u4f5c..." : "Requires Python/Java, databases, project experience, communication...",
      presets: isZh ? ["\u6821\u62db JD", "\u5b9e\u4e60 JD", "\u6682\u65e0 JD", "\u76ee\u6807\u516c\u53f8"] : ["Campus JD", "Internship JD", "No JD yet", "Target company"],
    },
  ];
}

function getQuestSteps() {
  return getModuleQuestSteps();
}

function getStepValue(step) {
  if (step.target === "role") return questState.role || document.getElementById("roleInput")?.value || "";
  if (step.target === "jd") return questState.jd || document.getElementById("jdInput")?.value || "";
  return questState.modules[step.id] || "";
}

function buildResumeTextFromModules() {
  const steps = getQuestSteps().filter((step) => step.target === "resume");
  const lines = steps
    .map((step) => {
      const value = (questState.modules[step.id] || "").trim();
      return value ? `${step.title.replace(/^.*?\uff1a/, "")}\n${value}` : "";
    })
    .filter(Boolean);
  return lines.join("\n\n");
}

function resetQuestStateFromFields() {
  questState.role = document.getElementById("roleInput")?.value?.trim() || "";
  questState.jd = document.getElementById("jdInput")?.value?.trim() || "";
  questState.modules = {};
  const rawResume = document.getElementById("resumeInput")?.value?.trim() || "";
  if (rawResume) questState.modules.evidence = rawResume;
}

function syncQuestToField() {
  const step = getQuestSteps()[questIndex];
  if (!step || !questAnswer) return;
  const value = questAnswer.value.trim();
  if (step.target === "role") {
    questState.role = value;
    const field = document.getElementById("roleInput");
    if (field) field.value = value;
  } else if (step.target === "jd") {
    questState.jd = value;
    const field = document.getElementById("jdInput");
    if (field) field.value = value;
  } else {
    questState.modules[step.id] = value;
    const field = document.getElementById("resumeInput");
    if (field) field.value = buildResumeTextFromModules();
  }
  renderLivePreview();
}

function renderModulePlan(steps) {
  if (!questModulePlan) return;
  questModulePlan.innerHTML = [
    `<span class="module-plan-label">${t("modulePlanLabel")}</span>`,
    ...steps.map((step, index) => {
      const done = getStepValue(step).trim() ? " is-done" : "";
      const active = index === questIndex ? " is-active" : "";
      return `<button class="module-pill${done}${active}" type="button" data-index="${index}">${index + 1}. ${step.title.replace(/^.*?\uff1a/, "").replace(/^Level \d+: /, "")}</button>`;
    }),
  ].join("");
}

function renderLivePreview() {
  if (!previewRole || !previewTemplate || !previewModules) return;
  const role = questState.role || document.getElementById("roleInput")?.value?.trim() || t("fallbackTargetRole");
  const templateName = currentTemplateName();
  if (previewSheet) {
    previewSheet.className = `preview-sheet template-${templateName}`;
  }
  previewRole.textContent = role;
  previewTemplate.textContent = `${getTemplateLabel()} · ${templatePreviewNote(templateName)}`;
  const steps = getQuestSteps();
  const blocks = steps
    .filter((step) => step.target !== "role")
    .map((step) => {
      const value = getStepValue(step).trim();
      const body = renderPreviewBody(step, value);
      return `<article class="preview-module preview-${step.id}${value ? " is-filled" : ""}">
        <span>${previewSectionTitle(step)}</span>
        <div class="preview-body">${body}</div>
      </article>`;
    })
    .join("");
  previewModules.innerHTML = blocks;
}

function renderQuest() {
  if (!questAnswer || !questTitle || !questPrompt) return;
  const steps = getQuestSteps();
  const step = steps[questIndex];
  renderModulePlan(steps);
  questTitle.textContent = step.title;
  questPrompt.textContent = step.prompt;
  questAnswer.placeholder = step.placeholder;
  questAnswer.value = getStepValue(step);
  questBadge.textContent = `${questIndex + 1} / ${steps.length}`;
  questProgress.style.width = `${((questIndex + 1) / steps.length) * 100}%`;
  questPrevButton.disabled = questIndex === 0;
  questNextButton.hidden = questIndex === steps.length - 1;
  questRunButton.hidden = questIndex !== steps.length - 1;
  questChips.innerHTML = step.presets
    .map((item) => `<button class="quest-chip" type="button" data-value="${item}">${item}</button>`)
    .join("");
  renderLivePreview();
}

function nextQuestStep(direction) {
  syncQuestToField();
  const steps = getQuestSteps();
  questIndex = Math.max(0, Math.min(steps.length - 1, questIndex + direction));
  renderQuest();
}

const pageAliases = {
  hero: "home",
  home: "home",
  lab: "quest",
  resume: "quest",
  quest: "quest",
  workspace: "workspace",
  signals: "workspace",
  opportunities: "opportunities",
};

function routeFromHash() {
  const raw = window.location.hash.replace("#", "").trim();
  return pageAliases[raw] || "home";
}

function setActivePage(page) {
  const activePage = pageAliases[page] || "home";
  document.querySelectorAll(".app-page").forEach((section) => {
    section.classList.toggle("is-active", section.dataset.page === activePage);
  });

  document.querySelectorAll("[data-route]").forEach((link) => {
    link.classList.toggle("is-active", link.dataset.route === activePage);
  });
}

document.querySelectorAll("[data-route]").forEach((link) => {
  link.addEventListener("click", (event) => {
    const nextPage = event.currentTarget.dataset.route;
    if (!nextPage) return;
    event.preventDefault();
    if (window.location.hash !== `#${nextPage}`) {
      window.location.hash = nextPage;
    } else {
      setActivePage(nextPage);
    }
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
});

window.addEventListener("hashchange", () => {
  setActivePage(routeFromHash());
  window.scrollTo({ top: 0, behavior: "smooth" });
});

function mountAmbientParticles() {
  const host = document.querySelector(".ambient-particles");
  if (!host || host.children.length) return;
  const particles = [
    [10, 8, 18, -1],
    [6, 18, 72, -7],
    [14, 28, 24, -4],
    [7, 38, 82, -10],
    [9, 47, 16, -3],
    [16, 58, 68, -12],
    [6, 68, 30, -6],
    [12, 78, 78, -15],
    [8, 88, 20, -9],
    [15, 92, 58, -2],
    [5, 14, 46, -13],
    [9, 33, 58, -5],
    [7, 52, 88, -16],
    [11, 72, 8, -11],
    [4, 24, 10, -17],
    [8, 64, 44, -8],
    [13, 84, 88, -14],
    [5, 44, 36, -6],
  ];

  particles.forEach(([size, x, y, delay], index) => {
    const node = document.createElement("span");
    node.className = "ambient-particle";
    node.style.setProperty("--size", `${size}px`);
    node.style.setProperty("--x", `${x}%`);
    node.style.setProperty("--y", `${y}%`);
    node.style.setProperty("--delay", `${delay}s`);
    node.style.setProperty("--duration", `${16 + (index % 5) * 3}s`);
    host.appendChild(node);
  });
}

document.addEventListener("pointermove", (event) => {
  const host = document.querySelector(".ambient-particles");
  if (!host) return;
  host.style.setProperty("--particle-x", `${Math.round((event.clientX / window.innerWidth) * 100)}%`);
  host.style.setProperty("--particle-y", `${Math.round((event.clientY / window.innerHeight) * 100)}%`);
});

document.querySelectorAll("[data-tilt-card]").forEach((card) => {
  card.addEventListener("pointermove", (event) => {
    const rect = card.getBoundingClientRect();
    const x = (event.clientX - rect.left) / rect.width - 0.5;
    const y = (event.clientY - rect.top) / rect.height - 0.5;
    card.style.setProperty("--tilt-x", `${(-y * 7).toFixed(2)}deg`);
    card.style.setProperty("--tilt-y", `${(x * 8).toFixed(2)}deg`);
  });

  card.addEventListener("pointerleave", () => {
    card.style.setProperty("--tilt-x", "0deg");
    card.style.setProperty("--tilt-y", "0deg");
  });
});

mountAmbientParticles();
applyLanguage(languageSelect.value);
setActivePage(routeFromHash());
loadDashboard();
loadWorkbenchSample();
resetQuestStateFromFields();
loadLocalizedExamples();
renderQuest();
renderGenerationResult(null);

languageSelect.addEventListener("change", (event) => {
  applyLanguage(event.target.value);
  loadDashboard();
  loadWorkbenchSample();
  resetQuestStateFromFields();
  loadLocalizedExamples();
  questIndex = 0;
  renderQuest();
  renderGenerationResult(null);
});

document.getElementById("loadSampleButton").addEventListener("click", () => {
  loadWorkbenchSample();
  resetQuestStateFromFields();
  renderQuest();
});

questAnswer?.addEventListener("input", syncQuestToField);
questDisciplineSelect?.addEventListener("change", () => {
  syncQuestToField();
  questState.modules = {};
  questIndex = 0;
  renderQuest();
});
templateSelect?.addEventListener("change", renderLivePreview);
questModulePlan?.addEventListener("click", (event) => {
  const pill = event.target.closest("[data-index]");
  if (!pill) return;
  syncQuestToField();
  questIndex = Number(pill.dataset.index);
  renderQuest();
});
["roleInput", "resumeInput", "jdInput"].forEach((id) => {
  document.getElementById(id)?.addEventListener("input", (event) => {
    if (id === "roleInput") questState.role = event.target.value.trim();
    if (id === "jdInput") questState.jd = event.target.value.trim();
    if (id === "resumeInput") questState.modules.evidence = event.target.value.trim();
    renderQuest();
  });
});
questPrevButton?.addEventListener("click", () => nextQuestStep(-1));
questNextButton?.addEventListener("click", () => nextQuestStep(1));
questRunButton?.addEventListener("click", () => {
  syncQuestToField();
  resumeWorkbenchForm.requestSubmit();
});
questChips?.addEventListener("click", (event) => {
  const chip = event.target.closest(".quest-chip");
  if (!chip || !questAnswer) return;
  const current = questAnswer.value.trim();
  const value = chip.dataset.value || "";
  const isAddProject = value === "\u65b0\u589e\u4e00\u4e2a\u9879\u76ee" || value === "Add another project";
  if (isAddProject) {
    const label = currentLocale() === "zh-CN" ? "\u9879\u76ee" : "Project";
    const nextIndex = Math.max(2, splitProjectBlocks(current).length + 1);
    questAnswer.value = current ? `${current}\n\n${label} ${nextIndex}: ` : `${label} 1: `;
  } else {
    questAnswer.value = current ? `${current}\n${value}` : value;
  }
  syncQuestToField();
  questAnswer.focus();
});

resumeWorkbenchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  renderWorkbench(await postJson("/api/resume-workbench", collectWorkbenchInput()));
});

document.getElementById("saveWorkbenchVersionButton").addEventListener("click", async (event) => {
  const snapshot = await setButtonBusy(
    event.currentTarget,
    t("savingVersion"),
    postJson("/api/resume-workbench/save", {
      ...collectWorkbenchInput(),
      generate_document: false,
    }),
  );
  if (snapshot.workbench_payload) renderWorkbench(snapshot.workbench_payload);
  renderGenerationResult(snapshot.generation_result || null);
  renderDashboard(snapshot);
});

document.getElementById("generateWorkbenchDocumentButton").addEventListener("click", async (event) => {
  const snapshot = await setButtonBusy(
    event.currentTarget,
    t("generatingFile"),
    postJson("/api/resume-workbench/save", {
      ...collectWorkbenchInput(),
      generate_document: true,
    }),
  );
  if (snapshot.workbench_payload) {
    renderWorkbench({
      ...snapshot.workbench_payload,
      generation_result: snapshot.generation_result || null,
    });
  } else {
    renderGenerationResult(snapshot.generation_result || null);
  }
  renderDashboard(snapshot);
  downloadGeneratedFile(snapshot.generation_result || null);
});

rawIntakeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  renderDashboard(await postJson("/api/intake/raw", {
    full_name: document.getElementById("profileFullName").value.trim() || t("fallbackCandidate"),
    target_title: document.getElementById("profileTargetTitle").value.trim() || t("fallbackTargetRole"),
    target_markets: document.getElementById("profileTargetMarkets").value.trim() || t("fallbackGlobal"),
    education: document.getElementById("intakeEducation").value.trim(),
    major: document.getElementById("intakeMajor").value.trim(),
    graduation_cycle: document.getElementById("intakeGraduationCycle").value.trim(),
    raw_text: document.getElementById("intakeRawText").value.trim(),
  }));
});

profileForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  renderDashboard(await postJson("/api/profile", {
    full_name: document.getElementById("profileFullName").value.trim(),
    target_title: document.getElementById("profileTargetTitle").value.trim(),
    target_markets: document.getElementById("profileTargetMarkets").value.trim(),
    strengths: document.getElementById("profileStrengths").value.trim(),
  }));
});

targetForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  renderDashboard(await postJson("/api/targets", {
    title: document.getElementById("targetTitle").value.trim(),
    market: document.getElementById("targetMarket").value.trim(),
    seniority: document.getElementById("targetSeniority").value.trim(),
    priorities: document.getElementById("targetPriorities").value.trim(),
  }));
  resetForm("targetForm");
});

resumeVersionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  renderDashboard(await postJson("/api/resume-versions", {
    label: document.getElementById("resumeVersionLabel").value.trim(),
    status: document.getElementById("resumeVersionStatus").value.trim(),
    focus: document.getElementById("resumeVersionFocus").value.trim(),
    market: document.getElementById("resumeVersionMarket").value.trim(),
  }));
  resetForm("resumeVersionForm");
});

applicationForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  renderDashboard(await postJson("/api/applications", {
    company: document.getElementById("applicationCompany").value.trim(),
    role: document.getElementById("applicationRole").value.trim(),
    stage: document.getElementById("applicationStage").value.trim(),
    next_step: document.getElementById("applicationNextStep").value.trim(),
  }));
  resetForm("applicationForm");
});

applicationFeedbackForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  renderDashboard(await postJson("/api/applications/feedback", {
    company: document.getElementById("feedbackCompany").value.trim(),
    role: document.getElementById("feedbackRole").value.trim(),
    result: document.getElementById("feedbackResult").value.trim(),
    feedback_notes: document.getElementById("feedbackNotes").value.trim(),
  }));
  resetForm("applicationFeedbackForm");
});

opportunityForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  renderDashboard(await postJson("/api/opportunities", {
    company: document.getElementById("opportunityCompany").value.trim(),
    title: document.getElementById("opportunityTitle").value.trim(),
    market: document.getElementById("opportunityMarket").value.trim(),
    location: document.getElementById("opportunityLocation").value.trim(),
    source: document.getElementById("opportunitySource").value.trim(),
    description: document.getElementById("opportunityDescription").value.trim(),
  }));
  resetForm("opportunityForm");
});

document.getElementById("batchOpportunityButton").addEventListener("click", async () => {
  let opportunities = [];
  try {
    opportunities = JSON.parse(document.getElementById("batchOpportunityInput").value.trim() || "[]");
  } catch (error) {
    return;
  }
  renderDashboard(await postJson("/api/opportunities/batch", { opportunities }));
});
