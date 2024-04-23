INSERT INTO starrs."SECTION" ("SECTION_NO", "COURSE_NO", "SEMESTER", "YEAR", "INSTRUCTOR_ID")
SELECT 
    CASE 
        WHEN row_number() OVER () < 10 THEN row_number() OVER ()
        WHEN row_number() OVER () < 100 THEN row_number() OVER ()
        ELSE row_number() OVER ()
    END AS "SECTION_NO",
    c."COURSE_NO",
    CASE 
        WHEN (random() * 3)::int = 0 THEN 'Wi'
        WHEN (random() * 3)::int = 1 THEN 'Fa'
        ELSE 'Su'
    END AS "SEMESTER",
    2023 + (random() * 5)::int AS "YEAR",
    CASE 
        WHEN (random() * 3)::int = 0 THEN '500500'
        WHEN (random() * 3)::int = 1 THEN '555555'
        ELSE '600000'
    END AS "INSTRUCTOR_ID"
FROM 
    starrs."COURSE" c
CROSS JOIN 
    generate_series(1, 10);