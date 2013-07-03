'Google Mock' mocks generator based on libclang:

usage:
    ./gmock.py [directory] [limit_to_interfaces_within_namespace]

example:
    find . -iname *.hpp | xargs ./gmock.py generated "Component"

