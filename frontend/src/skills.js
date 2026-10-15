// The same 48 skills and patterns as pipeline/tag/skills.py, so a CV is tagged
// exactly the way job adverts are. If you change one file, change the other
// (tests: src/skills.test.mjs and the Python examples in docs/SKILLS.md).

const ci = (p) => new RegExp(p, 'i') // case-insensitive
const cs = (p) => new RegExp(p)      // case-sensitive

export const SKILLS = [
  // Languages
  ['SQL', 'Languages', [ci('\\bsql\\b')]],
  ['T-SQL', 'Languages', [ci('\\bt-?sql\\b')]],
  ['Python', 'Languages', [ci('\\bpython\\b')]],
  ['R', 'Languages', [cs('(?<![&\\w])R(?![&\\w])')]],
  ['DAX', 'Languages', [ci('\\bdax\\b')]],
  ['VBA', 'Languages', [ci('\\bvba\\b|\\bmacros?\\b')]],
  // BI tools
  ['Power BI', 'BI tools', [ci('power\\s?bi|\\bpbi\\b')]],
  ['Power Query', 'BI tools', [ci('power\\s?query')]],
  ['Excel', 'BI tools', [cs('\\b(?:Excel|EXCEL)\\b(?!\\s+(?:in|at|as|across)\\b)')]],
  ['Tableau', 'BI tools', [ci('\\btableau\\b')]],
  ['Looker', 'BI tools', [ci('\\blooker\\b')]],
  ['Qlik', 'BI tools', [ci('\\bqlik')]],
  ['SSRS', 'BI tools', [ci('\\bssrs\\b')]],
  ['Google Analytics', 'BI tools', [ci('google analytics|\\bga4\\b')]],
  // Microsoft data platform
  ['Azure', 'Microsoft data platform', [ci('\\bazure\\b')]],
  ['Microsoft Fabric', 'Microsoft data platform', [ci('microsoft fabric'), cs('\\bFabric\\b')]],
  ['Synapse', 'Microsoft data platform', [ci('\\bsynapse\\b')]],
  ['Data Factory', 'Microsoft data platform', [ci('data factory|\\badf\\b')]],
  ['SQL Server', 'Microsoft data platform', [ci('sql server|\\bmssql\\b')]],
  ['SSIS', 'Microsoft data platform', [ci('\\bssis\\b')]],
  ['SSAS', 'Microsoft data platform', [ci('\\bssas\\b')]],
  ['Power Automate', 'Microsoft data platform', [ci('power\\s?automate')]],
  ['Power Apps', 'Microsoft data platform', [ci('power\\s?apps')]],
  ['SharePoint', 'Microsoft data platform', [ci('sharepoint')]],
  // Cloud and data platforms
  ['Databricks', 'Cloud and data platforms', [ci('databricks')]],
  ['Snowflake', 'Cloud and data platforms', [ci('snowflake')]],
  ['AWS', 'Cloud and data platforms', [ci('\\baws\\b|amazon web services|redshift')]],
  ['Google Cloud', 'Cloud and data platforms', [ci('\\bgcp\\b|google cloud|bigquery')]],
  ['PostgreSQL', 'Cloud and data platforms', [ci('postgres')]],
  ['MySQL', 'Cloud and data platforms', [ci('\\bmysql\\b')]],
  ['dbt', 'Cloud and data platforms', [ci('\\bdbt\\b')]],
  ['Airflow', 'Cloud and data platforms', [ci('airflow')]],
  ['Spark', 'Cloud and data platforms', [cs('\\bSpark\\b'), ci('pyspark|apache spark')]],
  ['Alteryx', 'Cloud and data platforms', [ci('alteryx')]],
  ['SAS', 'Cloud and data platforms', [ci('\\bsas\\b')]],
  ['SPSS', 'Cloud and data platforms', [ci('\\bspss\\b')]],
  // Concepts
  ['Data modelling', 'Concepts', [ci('data model')]],
  ['Data warehousing', 'Concepts', [ci('data\\s?warehous')]],
  ['ETL', 'Concepts', [ci('\\betl\\b|\\belt\\b')]],
  ['Statistics', 'Concepts', [ci('statistic')]],
  ['Machine learning', 'Concepts', [ci('machine learning|\\bml\\b')]],
  ['AI', 'Concepts', [ci('\\bai\\b|artificial intelligence|\\bgenai\\b|\\bllms?\\b')]],
  // Ways of working
  ['Agile', 'Ways of working', [ci('\\bagile\\b|\\bscrum\\b')]],
  ['Jira', 'Ways of working', [ci('\\bjira\\b')]],
  ['Git', 'Ways of working', [ci('\\bgit\\b|github|gitlab')]],
  // Business apps
  ['Salesforce', 'Business apps', [ci('salesforce')]],
  ['Dynamics 365', 'Business apps', [ci('(?:microsoft )?dynamics\\s?(?:365|crm|ax|nav|f&o|bc)|microsoft dynamics')]],
  ['SAP', 'Business apps', [ci('\\bsap\\b')]],
]

export function findSkills(text) {
  const t = text || ''
  return new Set(SKILLS.filter(([, , res]) => res.some((re) => re.test(t))).map(([name]) => name))
}

// Skills that stand in for each other well enough to count as "close".
// Having one of a group when a role asks for another counts as half.
export const SIBLINGS = [
  ['Power BI', 'Tableau', 'Looker', 'Qlik'],
  ['SQL', 'T-SQL', 'SQL Server', 'PostgreSQL', 'MySQL'],
  ['Azure', 'Microsoft Fabric', 'Synapse', 'Data Factory', 'AWS', 'Google Cloud'],
  ['Databricks', 'Snowflake', 'Spark'],
  ['Python', 'R'],
  ['SSIS', 'Data Factory', 'ETL', 'dbt'],
  ['SSRS', 'Power BI'],
  ['DAX', 'Power Query'],
  ['Statistics', 'SPSS', 'SAS', 'R'],
  ['Data warehousing', 'Data modelling'],
]
