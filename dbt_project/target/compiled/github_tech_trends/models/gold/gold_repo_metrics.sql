

select
    repo_id,
    repo_name,
    stargazers_count,
    forks_count,
    (stargazers_count + forks_count) as engagement_score,
    current_timestamp as updated_at
from "github_analytics"."main"."stg_github_repos"


  where extracted_at > (select max(updated_at) from "github_analytics"."main"."gold_repo_metrics")
