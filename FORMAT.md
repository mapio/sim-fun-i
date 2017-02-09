RESULTS :=  [ ( RESULT )+ ]

RESULT := {
    'signature': {
        # these fields are the "signature" collected by "Tristo mietitore"
        'uid': <UID>,
        'info': <INFO>,
        'ip': <EXTRA>
    },
    'exercises': [ ( <EXERCISE> )+ ]
}

EXERCISE := {
    'name', <EXERCISE_NAME>,
    'sources': [ ( <SOURCE> )+ ],
    'cases': [ <COMPILATION_CASE>, ( <CASE> )* ]
}

SOURCE := {
    'name': <SOURCE_NAME>,
    'content': <CONTENT>
}

CASE := { # these fields are TestCase.KINDS
    'name': <CASE_NAME>,
    'args': <ARGS_CONTENT>,
    'input': <INPUT_CONTENT>,
    'expected': <EXPECTED_CONTENT>,
    'actual': <ACTUAL_CONTENT>,
    'diffs': <DIFFS_CONTENT>,
    'errors': <ERRORS_CONTENT>
}
