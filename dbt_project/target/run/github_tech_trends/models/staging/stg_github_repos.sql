
        
            delete from "github_analytics"."main"."stg_github_repos"
            where (
                repo_id) in (
                select (repo_id)
                from "stg_github_repos__dbt_tmp20260729072348511383"
            );

        
    

    insert into "github_analytics"."main"."stg_github_repos" ("repo_id", "repo_name", "full_name", "stargazers_count", "forks_count", "open_issues_count", "updated_at", "extracted_at")
    (
        select "repo_id", "repo_name", "full_name", "stargazers_count", "forks_count", "open_issues_count", "updated_at", "extracted_at"
        from "stg_github_repos__dbt_tmp20260729072348511383"
    )
  