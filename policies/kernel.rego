package kernel.authz

import rego.v1

default allow = false

# Deontic Prohibitions
allow = false if {
    input.action.object.name == "payroll"
}

allow = false if {
    input.action.object.name == "nuclear_launch_codes"
}

# Allow if trust is high and not prohibited
allow = true if {
    input.context.trust_score >= 0.5
    not prohibited
}

prohibited if {
    input.action.object.name == "payroll"
}

prohibited if {
    input.action.object.name == "nuclear_launch_codes"
}
