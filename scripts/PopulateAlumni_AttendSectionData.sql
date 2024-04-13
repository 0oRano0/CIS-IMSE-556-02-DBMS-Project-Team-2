-- Insert records for alumni users
INSERT INTO starrs."ATTENDS_SECTION" ("STUDENT_ID", "COURSE_NO", "SECTION_NO", "SEMESTER", "YEAR", "Grade", "Registration Status")
SELECT
    u."USER_ID",
    c."COURSE_NO",
    s."SECTION_NO",
    s."SEMESTER",
    s."YEAR",
    CASE
        WHEN RANDOM() < 0.25 THEN 3
        WHEN RANDOM() < 0.5 THEN 3.3
        WHEN RANDOM() < 0.75 THEN 3.6
        ELSE 4
    END AS "Grade",
    'Registered' AS "Registration Status"
FROM
    starrs."USER" u
    CROSS JOIN (
        SELECT DISTINCT ON ("COURSE_NO", "DEPARTMENT") "COURSE_NO", "DEPARTMENT"
        FROM starrs."COURSE"
    ) c
    JOIN (
        SELECT DISTINCT ON ("COURSE_NO") "COURSE_NO", "SECTION_NO", "SEMESTER", "YEAR"
        FROM starrs."SECTION"
    ) s ON c."COURSE_NO" = s."COURSE_NO"
WHERE
    u."FIRST_NAME" ILIKE '%alumni%'  -- Select alumni users
    AND NOT EXISTS (
        SELECT 1
        FROM starrs."ATTENDS_SECTION" AS att
        WHERE att."STUDENT_ID" = u."USER_ID"
            AND att."COURSE_NO" = c."COURSE_NO"
    )
LIMIT 60;  -- Limit total records to 60 (30 per user)
