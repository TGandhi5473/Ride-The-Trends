-- models/staging/stg_feedback.sql

WITH source AS (
    SELECT * FROM {{ source('raw_data', 'user_interactions') }}
),

renamed AS (
    SELECT
        id AS interaction_id,
        trend_id,
        bert_score,
        CASE 
            WHEN user_action = 'Approve' THEN 1.0
            WHEN user_action = 'Reject' THEN 0.0
            ELSE 0.5 
        END AS human_score,
        created_at AS feedback_at
    FROM source
),

-- Ensures the model is never empty so downstream joins don't fail
dummy_data AS (
    SELECT 
        'dummy' AS interaction_id,
        'dummy' AS trend_id,
        0.5 AS bert_score,
        0.5 AS human_score,
        CURRENT_TIMESTAMP AS feedback_at
    WHERE NOT EXISTS (SELECT 1 FROM renamed)
)

SELECT * FROM renamed
UNION ALL
SELECT * FROM dummy_data
