
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    

with child as (
    select repo_id as from_field
    from "github_analytics"."main"."gold_repo_metrics"
    where repo_id is not null
),

parent as (
    select repo_id as to_field
    from "github_analytics"."main"."stg_github_repos"
)

select
    from_field

from child
left join parent
    on child.from_field = parent.to_field

where parent.to_field is null



  
  
      
    ) dbt_internal_test