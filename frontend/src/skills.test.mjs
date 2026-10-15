// Run with: node src/skills.test.mjs  (same phrases as the Python tagger was tested on)
import { findSkills } from './skills.js'

const cases = [
  ['of a range of statistical techniques in R or Python (or SPSS) for examining', ['Python', 'R', 'SPSS', 'Statistics']],
  ['decisions across A&R, Marketing, Digital', []],
  ['outcomes- per squad R&Rs Profile Significant experience', []],
  ['Experience with Python/R, predictive analytics or machine learning', ['Machine learning', 'Python', 'R']],
  ['You will excel in a fast-paced team. Advanced Excel and PowerBI required.', ['Excel', 'Power BI']],
  ['Strong team dynamics; experience of Microsoft Dynamics 365 a plus', ['Dynamics 365']],
  ['part of the fabric of our business', []],
  ['Experience with Microsoft Fabric lakehouses and Fabric pipelines', ['Microsoft Fabric']],
  ['spark ideas and curiosity', []],
  ['PySpark and Databricks; Spark SQL', ['Databricks', 'SQL', 'Spark']],
  ['Senior Power BI Developer', ['Power BI']],
  ['T-SQL, SQL Server, SSIS, SSRS and Azure Data Factory (ADF)', ['Azure', 'Data Factory', 'SQL', 'SQL Server', 'SSIS', 'SSRS', 'T-SQL']],
  ['excellent communication skills', []],
]

let failures = 0
for (const [text, expected] of cases) {
  const got = [...findSkills(text)].sort()
  const ok = JSON.stringify(got) === JSON.stringify([...expected].sort())
  if (!ok) failures++
  console.log(ok ? 'OK ' : 'XX ', got.join(', ') || '(none)', '|', text.slice(0, 55))
}
console.log('failures', failures)
process.exit(failures ? 1 : 0)
