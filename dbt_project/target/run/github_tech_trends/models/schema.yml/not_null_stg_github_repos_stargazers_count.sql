
    
    select
      count(*) as failures,
      count(*) != 0 as should_warn,
      count(*) != 0 as should_error
    from (
      
    
  
    
    



select stargazers_count
from "github_analytics"."main"."stg_github_repos"
where stargazers_count is null



  
  
      
    ) dbt_internal_test