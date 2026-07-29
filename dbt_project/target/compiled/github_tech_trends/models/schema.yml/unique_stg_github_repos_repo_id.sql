
    
    

select
    repo_id as unique_field,
    count(*) as n_records

from "github_analytics"."main"."stg_github_repos"
where repo_id is not null
group by repo_id
having count(*) > 1


