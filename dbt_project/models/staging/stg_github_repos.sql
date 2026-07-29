{{
    config(
        materialized='incremental',
        unique_key='repo_id'
    )
}}

with source_data as (
    select
        id as repo_id,
        name as repo_name,
        full_name,
        stargazers_count,
        forks_count,
        open_issues_count,
        updated_at,
        extracted_at,
        row_number() over (
            partition by id 
            order by extracted_at desc, updated_at desc
        ) as rn
    from {{ source('github_raw', 'raw_repos') }}
)

select
    repo_id,
    repo_name,
    full_name,
    stargazers_count,
    forks_count,
    open_issues_count,
    updated_at,
    extracted_at
from source_data
where rn = 1

{% if is_incremental() %}
  and extracted_at > (select max(extracted_at) from {{ this }})
{% endif %}