-- Null
INSERT INTO starrs."ATTENDS_SECTION" ("STUDENT_ID", "COURSE_NO", "SECTION_NO", "SEMESTER", "YEAR", "Grade", "Registration Status")
SELECT DISTINCT ON (u."USER_ID", c."COURSE_NO")
    u."USER_ID",
    c."COURSE_NO",
    s."SECTION_NO",
    s."SEMESTER",
    s."YEAR",
    NULL AS "Grade",
    NULL AS "Registration Status"
FROM
    starrs."USER" u
CROSS JOIN (
    SELECT DISTINCT "COURSE_NO"
    FROM starrs."COURSE"
) c
JOIN (
    SELECT DISTINCT ON ("COURSE_NO") "COURSE_NO", "SECTION_NO", "SEMESTER", "YEAR"
    FROM starrs."SECTION"
) s ON c."COURSE_NO" = s."COURSE_NO"
WHERE
    u."FIRST_NAME" ILIKE '%student%'  -- Select user IDs with "student" in their first name
    AND NOT EXISTS (
        SELECT 1
        FROM starrs."ATTENDS_SECTION" AS att
        WHERE att."STUDENT_ID" = u."USER_ID"
            AND att."COURSE_NO" = c."COURSE_NO"
    )
LIMIT 10;

-- Pending
INSERT INTO starrs."ATTENDS_SECTION" ("STUDENT_ID", "COURSE_NO", "SECTION_NO", "SEMESTER", "YEAR", "Grade", "Registration Status")
SELECT DISTINCT ON (u."USER_ID", c."COURSE_NO")
    u."USER_ID",
    c."COURSE_NO",
    s."SECTION_NO",
    s."SEMESTER",
    s."YEAR",
    NULL AS "Grade",
    'Pending' AS "Registration Status"
FROM
    starrs."USER" u
CROSS JOIN (
    SELECT DISTINCT "COURSE_NO"
    FROM starrs."COURSE"
) c
JOIN (
    SELECT DISTINCT ON ("COURSE_NO") "COURSE_NO", "SECTION_NO", "SEMESTER", "YEAR"
    FROM starrs."SECTION"
) s ON c."COURSE_NO" = s."COURSE_NO"
WHERE
    u."FIRST_NAME" ILIKE '%student%'  -- Select user IDs with "student" in their first name
    AND NOT EXISTS (
        SELECT 1
        FROM starrs."ATTENDS_SECTION" AS att
        WHERE att."STUDENT_ID" = u."USER_ID"
            AND att."COURSE_NO" = c."COURSE_NO"
    )
LIMIT 10;

-- Dropped
INSERT INTO starrs."ATTENDS_SECTION" ("STUDENT_ID", "COURSE_NO", "SECTION_NO", "SEMESTER", "YEAR", "Grade", "Registration Status")
SELECT DISTINCT ON (u."USER_ID", c."COURSE_NO")
    u."USER_ID",
    c."COURSE_NO",
    s."SECTION_NO",
    s."SEMESTER",
    s."YEAR",
    CASE 
        WHEN RANDOM() < 0.5 THEN 2.6
        ELSE 2.3
    END AS "Grade",
    'Dropped' AS "Registration Status"
FROM
    starrs."USER" u
CROSS JOIN (
    SELECT DISTINCT "COURSE_NO"
    FROM starrs."COURSE"
) c
JOIN (
    SELECT DISTINCT ON ("COURSE_NO") "COURSE_NO", "SECTION_NO", "SEMESTER", "YEAR"
    FROM starrs."SECTION"
) s ON c."COURSE_NO" = s."COURSE_NO"
WHERE
    u."FIRST_NAME" ILIKE '%student%'  -- Select user IDs with "student" in their first name
    AND NOT EXISTS (
        SELECT 1
        FROM starrs."ATTENDS_SECTION" AS att
        WHERE att."STUDENT_ID" = u."USER_ID"
            AND att."COURSE_NO" = c."COURSE_NO"
    )
LIMIT 5;

-- Registered
INSERT INTO starrs."ATTENDS_SECTION" ("STUDENT_ID", "COURSE_NO", "SECTION_NO", "SEMESTER", "YEAR", "Grade", "Registration Status")
SELECT DISTINCT ON (u."USER_ID", c."COURSE_NO")
    u."USER_ID",
    c."COURSE_NO",
    s."SECTION_NO",
    s."SEMESTER",
    s."YEAR",
    CASE 
        WHEN RANDOM() < 0.5 THEN 4.0
        WHEN RANDOM() < 0.7 THEN 3.3
        ELSE 2.0
    END AS "Grade",
    'Registered' AS "Registration Status"
FROM
    starrs."USER" u
CROSS JOIN (
    SELECT DISTINCT "COURSE_NO"
    FROM starrs."COURSE"
) c
JOIN (
    SELECT DISTINCT ON ("COURSE_NO") "COURSE_NO", "SECTION_NO", "SEMESTER", "YEAR"
    FROM starrs."SECTION"
) s ON c."COURSE_NO" = s."COURSE_NO"
WHERE
    u."FIRST_NAME" ILIKE '%student%'  -- Select user IDs with "student" in their first name
    AND NOT EXISTS (
        SELECT 1
        FROM starrs."ATTENDS_SECTION" AS att
        WHERE att."STUDENT_ID" = u."USER_ID"
            AND att."COURSE_NO" = c."COURSE_NO"
    )
LIMIT 200;
