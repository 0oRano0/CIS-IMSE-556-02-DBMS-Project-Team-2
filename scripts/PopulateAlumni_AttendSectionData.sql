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
    'Completed' AS "Registration Status"
FROM
    starrs."USER" u
    CROSS JOIN (
        SELECT "COURSE_NO", "DEPARTMENT" FROM starrs."COURSE" WHERE "COURSE_NO" IN (510, 511, 5212, 513) -- Include CS510, CS511, IMSE5212, IMSE513
        UNION ALL
        SELECT "COURSE_NO", "DEPARTMENT" FROM (
            SELECT "COURSE_NO", "DEPARTMENT" FROM starrs."COURSE" WHERE "COURSE_NO" NOT IN (510, 511, 5212, 513) -- Select rest of the courses
            ORDER BY RANDOM() LIMIT 20 -- Limit total additional records to 20
        ) AS rest_courses
    ) AS selected_courses
    JOIN (
        SELECT DISTINCT ON ("COURSE_NO") "COURSE_NO", "SECTION_NO", "SEMESTER", "YEAR"
        FROM starrs."SECTION"
        WHERE "YEAR" <= 2023  -- Filter out sections with year greater than 2023
    ) s ON selected_courses."COURSE_NO" = s."COURSE_NO"
    JOIN starrs."COURSE" c ON selected_courses."COURSE_NO" = c."COURSE_NO"
WHERE
    u."FIRST_NAME" ILIKE '%alumni%'  -- Select alumni users
    AND NOT EXISTS (
        SELECT 1
        FROM starrs."ATTENDS_SECTION" AS att
        WHERE att."STUDENT_ID" = u."USER_ID"
            AND att."COURSE_NO" = selected_courses."COURSE_NO"
    );
