
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select repo_id
from "github_analytics"."main"."gold_repo_metrics"
where repo_id is null



  
  
      
    ) dbt_internal_test