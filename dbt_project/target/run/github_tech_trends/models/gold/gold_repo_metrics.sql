
        
            delete from "github_analytics"."main"."gold_repo_metrics"
            where (
                repo_id) in (
                select (repo_id)
                from "gold_repo_metrics__dbt_tmp20260729072403909965"
            );

        
    

    insert into "github_analytics"."main"."gold_repo_metrics" ("repo_id", "repo_name", "stargazers_count", "forks_count", "engagement_score", "updated_at")
    (
        select "repo_id", "repo_name", "stargazers_count", "forks_count", "engagement_score", "updated_at"
        from "gold_repo_metrics__dbt_tmp20260729072403909965"
    )
  