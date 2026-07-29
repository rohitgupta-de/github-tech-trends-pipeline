
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select engagement_score
from "github_analytics"."main"."gold_repo_metrics"
where engagement_score is null



  
  
      
    ) dbt_internal_test