
    
    

select
    repo_id as unique_field,
    count(*) as n_records

from "github_analytics"."main"."gold_repo_metrics"
where repo_id is not null
group by repo_id
having count(*) > 1


