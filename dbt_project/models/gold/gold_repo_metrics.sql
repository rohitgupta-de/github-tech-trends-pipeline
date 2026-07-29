{{
    config(
        materialized='incremental',
        unique_key='repo_id'
    )
}}

select
    repo_id,
    repo_name,
    stargazers_count,
    forks_count,
    (stargazers_count + forks_count) as engagement_score,
    current_timestamp as updated_at
from {{ ref('stg_github_repos') }}

{% if is_incremental() %}
  where extracted_at > (select max(updated_at) from {{ this }})
{% endif %}