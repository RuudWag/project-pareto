#####################################################################################################
# PARETO was produced under the DOE Produced Water Application for Beneficial Reuse Environmental
# Impact and Treatment Optimization (PARETO), and is copyright (c) 2021 by the software owners: The
# Regents of the University of California, through Lawrence Berkeley National Laboratory, et al. All
# rights reserved.
#
# NOTICE. This Software was developed under funding from the U.S. Department of Energy and the
# U.S. Government consequently retains certain rights. As such, the U.S. Government has been granted
# for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license
# in the Software to reproduce, distribute copies to the public, prepare derivative works, and perform
# publicly and display publicly, and to permit other to do so.
#####################################################################################################
"""
Test strategic model
"""
# Import Pyomo libraries
import pyomo.environ as pyo
from pyomo.util.check_units import assert_units_consistent
from pyomo.core.base import value
from pyomo.environ import Constraint

# Import IDAES solvers
from pareto.utilities.solvers import get_solver
from pareto.strategic_water_management.strategic_produced_water_optimization import (
    create_model,
    solve_model,
    get_strategic_model_unit_container,
    Objectives,
    scale_model,
    PipelineCost,
    PipelineCapacity,
    IncludeNodeCapacity,
)
from pareto.utilities.get_data import get_data
from pareto.utilities.units_support import (
    flatten_list,
    PintUnitExtractionVisitor,
)
from importlib import resources
import pytest
from idaes.core.util.model_statistics import degrees_of_freedom

__author__ = "Pareto Team (Andres Calderon, M. Zamarripa)"

# -----------------------------------------------------------------------------
# Get default solver for testing
solver = get_solver("cbc")
# -----------------------------------------------------------------------------


@pytest.fixture(scope="module")
def build_strategic_model():
    # This emulates what the pyomo command-line tools does
    # Tabs in the input Excel spreadsheet
    set_list = [
        "ProductionPads",
        "ProductionTanks",
        "CompletionsPads",
        "SWDSites",
        "FreshwaterSources",
        "StorageSites",
        "TreatmentSites",
        "ReuseOptions",
        "NetworkNodes",
        "PipelineDiameters",
        "StorageCapacities",
        "InjectionCapacities",
        "TreatmentCapacities",
    ]
    parameter_list = [
        "Units",
        "PNA",
        "CNA",
        "CCA",
        "NNA",
        "NCA",
        "NKA",
        "NRA",
        "NSA",
        "FCA",
        "RCA",
        "RNA",
        "SNA",
        "PCT",
        "PKT",
        "FCT",
        "CST",
        "CCT",
        "CKT",
        "TruckingTime",
        "CompletionsDemand",
        "PadRates",
        "FlowbackRates",
        "NodeCapacities",
        "InitialPipelineCapacity",
        "InitialDisposalCapacity",
        "InitialTreatmentCapacity",
        "FreshwaterSourcingAvailability",
        "PadOffloadingCapacity",
        "CompletionsPadStorage",
        "DisposalOperationalCost",
        "TreatmentOperationalCost",
        "ReuseOperationalCost",
        "PipelineOperationalCost",
        "FreshSourcingCost",
        "TruckingHourlyCost",
        "PipelineDiameterValues",
        "DisposalCapacityIncrements",
        "InitialStorageCapacity",
        "StorageCapacityIncrements",
        "TreatmentCapacityIncrements",
        "TreatmentEfficiency",
        "DisposalExpansionCost",
        "StorageExpansionCost",
        "TreatmentExpansionCost",
        "PipelineCapexDistanceBased",
        "PipelineCapexCapacityBased",
        "PipelineCapacityIncrements",
        "PipelineExpansionDistance",
        "Hydraulics",
        "Economics",
        "PadWaterQuality",
        "StorageInitialWaterQuality",
    ]

    # note the double backslashes '\\' in that path reference
    with resources.path(
        "pareto.case_studies",
        "input_data_generic_strategic_case_study_LAYFLAT_FULL.xlsx",
    ) as fpath:
        [df_sets, df_parameters] = get_data(fpath, set_list, parameter_list)

        # create mathematical model
        def _call_model_with_config(config_dict):
            strategic_model = create_model(df_sets, df_parameters, config_dict)
            return strategic_model

    return _call_model_with_config


@pytest.mark.unit
def test_basic_build_capex_distance_based_capacity_input(build_strategic_model):
    """Make a model and make sure it doesn't throw exception"""
    m = build_strategic_model(
        config_dict={
            "objective": Objectives.cost,
            "pipeline_cost": PipelineCost.distance_based,
            "pipeline_capacity": PipelineCapacity.input,
            "node_capacity": IncludeNodeCapacity.true,
        }
    )
    assert degrees_of_freedom(m) == 64051
    # Check unit config arguments
    assert len(m.config) == 5
    assert m.config.objective
    assert isinstance(m.s_T, pyo.Set)
    assert isinstance(m.v_F_Piped, pyo.Var)
    assert isinstance(m.p_pi_Trucking, pyo.Param)
    assert isinstance(m.PipelineCapacityExpansion, pyo.Constraint)
    assert isinstance(m.PipelineExpansionCapEx, pyo.Constraint)


@pytest.mark.unit
def test_basic_build_capex_distance_based_capacity_calculated(build_strategic_model):
    """Make a model and make sure it doesn't throw exception"""
    m = build_strategic_model(
        config_dict={
            "objective": Objectives.cost,
            "pipeline_cost": PipelineCost.distance_based,
            "pipeline_capacity": PipelineCapacity.calculated,
            "node_capacity": IncludeNodeCapacity.true,
        }
    )
    assert degrees_of_freedom(m) == 64051
    # Check unit config arguments
    assert len(m.config) == 5
    assert m.config.objective
    assert isinstance(m.s_T, pyo.Set)
    assert isinstance(m.v_F_Piped, pyo.Var)
    assert isinstance(m.p_pi_Trucking, pyo.Param)
    assert isinstance(m.PipelineCapacityExpansion, pyo.Constraint)
    assert isinstance(m.PipelineExpansionCapEx, pyo.Constraint)


@pytest.mark.unit
def test_basic_build_capex_capacity_based_capacity_input(build_strategic_model):
    """Make a model and make sure it doesn't throw exception"""
    m = build_strategic_model(
        config_dict={
            "objective": Objectives.cost,
            "pipeline_cost": PipelineCost.capacity_based,
            "pipeline_capacity": PipelineCapacity.input,
            "node_capacity": IncludeNodeCapacity.true,
        }
    )
    assert degrees_of_freedom(m) == 64051
    # Check unit config arguments
    assert len(m.config) == 5
    assert m.config.objective
    assert isinstance(m.s_T, pyo.Set)
    assert isinstance(m.v_F_Piped, pyo.Var)
    assert isinstance(m.p_pi_Trucking, pyo.Param)
    assert isinstance(m.PipelineCapacityExpansion, pyo.Constraint)
    assert isinstance(m.PipelineExpansionCapEx, pyo.Constraint)


@pytest.mark.unit
def test_basic_build_capex_capacity_based_capacity_calculated(build_strategic_model):
    """Make a model and make sure it doesn't throw exception"""
    m = build_strategic_model(
        config_dict={
            "objective": Objectives.cost,
            "pipeline_cost": PipelineCost.capacity_based,
            "pipeline_capacity": PipelineCapacity.calculated,
            "node_capacity": IncludeNodeCapacity.true,
        }
    )
    assert degrees_of_freedom(m) == 64051
    # Check unit config arguments
    assert len(m.config) == 5
    assert m.config.objective
    assert isinstance(m.s_T, pyo.Set)
    assert isinstance(m.v_F_Piped, pyo.Var)
    assert isinstance(m.p_pi_Trucking, pyo.Param)
    assert isinstance(m.PipelineCapacityExpansion, pyo.Constraint)
    assert isinstance(m.PipelineExpansionCapEx, pyo.Constraint)


@pytest.mark.component
def test_strategic_model_unit_consistency(build_strategic_model):
    """
    Note: There are pyomo functions like assert_units_consistent that test consistency of expressions.
    This test utilizes assert_units_consistent in addition to a special case test assertion.
    The need for this special case comes from constraints that are mathematically the same, but are not
    interpreted as such by Pyomo. An example is the storage balance constraint in time period T:
    storage at time T [bbl] = flow in [bbl/week] - flow out [bbl/week] + storage at time T-1 [bbl]
    The time unit of the flow in and flow out rate variables will always be the same as the
    length of time T that is the decision period, so the units are consistent despite [bbl] and
    [bbl/day] being inconsistent.
    """
    m = build_strategic_model(
        config_dict={
            "objective": Objectives.cost,
            "pipeline_cost": PipelineCost.capacity_based,
            "pipeline_capacity": PipelineCapacity.calculated,
        }
    )

    # Create an instance of PintUnitExtractionVisitor that can assist with getting units from constraints
    visitor = PintUnitExtractionVisitor(get_strategic_model_unit_container())
    # Iterate through all Constraints
    for c in m.component_objects(Constraint):
        # If indexed, iterate through Constraint indexes
        for index in c:
            if index is None:
                condata = c

            elif index is not None:
                condata = c[index]

            # Obtain lower, upper, and body of constraint
            args = list()
            if condata.lower is not None and value(condata.lower) != 0.0:
                args.append(condata.lower)

            args.append(condata.body)

            if condata.upper is not None and value(condata.upper) != 0.0:
                args.append(condata.upper)
            # Use the visitor to extract the units of lower, upper,
            # and body of our constraint
            pint_units = [visitor.walk_expression(arg) for arg in args]
            # The units are in a nested list, flatten the list
            flat_list = flatten_list(pint_units)
            flat_list = [x for x in flat_list if x]

            # Compare all units to the first unit. Assess if the unique units are valid.
            first_unit = flat_list[0]
            # The decision period will be used to assess if the unit is valid
            decision_period_pint_unit = m.decision_period._get_pint_unit()
            for py_unit in flat_list[1:]:
                if visitor._equivalent_pint_units(first_unit, py_unit):
                    break
                # If the unit is equivalent when multiplying by the decision period,
                # the unit is consistent
                elif visitor._equivalent_pint_units(
                    first_unit * decision_period_pint_unit, py_unit
                ):
                    break
                elif visitor._equivalent_pint_units(
                    first_unit, py_unit * decision_period_pint_unit
                ):
                    break
                # otherwise, check if consistent with Pyomo's check
                else:
                    assert_units_consistent(condata)


# if solver cbc exists @solver
@pytest.mark.component
def test_run_strategic_model(build_strategic_model):
    m = build_strategic_model(
        config_dict={
            "objective": Objectives.cost,
            "pipeline_cost": PipelineCost.capacity_based,
            "pipeline_capacity": PipelineCapacity.calculated,
        }
    )
    solver = get_solver("cbc")
    solver.options["seconds"] = 60
    results = solver.solve(m, tee=False)
    assert degrees_of_freedom(m) == 64051


@pytest.fixture(scope="module")
def build_reduced_strategic_model():
    # This emulates what the pyomo command-line tools does
    # Tabs in the input Excel spreadsheet
    set_list = [
        "ProductionPads",
        "ProductionTanks",
        "CompletionsPads",
        "SWDSites",
        "FreshwaterSources",
        "StorageSites",
        "TreatmentSites",
        "ReuseOptions",
        "NetworkNodes",
        "PipelineDiameters",
        "StorageCapacities",
        "InjectionCapacities",
        "TreatmentCapacities",
    ]
    parameter_list = [
        "Units",
        "PNA",
        "CNA",
        "CCA",
        "NNA",
        "NCA",
        "NKA",
        "NRA",
        "NSA",
        "FCA",
        "RCA",
        "RNA",
        "SNA",
        "PCT",
        "PKT",
        "FCT",
        "CST",
        "CCT",
        "CKT",
        "TruckingTime",
        "CompletionsDemand",
        "PadRates",
        "FlowbackRates",
        "NodeCapacities",
        "InitialPipelineCapacity",
        "InitialDisposalCapacity",
        "InitialTreatmentCapacity",
        "FreshwaterSourcingAvailability",
        "PadOffloadingCapacity",
        "CompletionsPadStorage",
        "DisposalOperationalCost",
        "TreatmentOperationalCost",
        "ReuseOperationalCost",
        "PipelineOperationalCost",
        "FreshSourcingCost",
        "TruckingHourlyCost",
        "PipelineDiameterValues",
        "DisposalCapacityIncrements",
        "InitialStorageCapacity",
        "StorageCapacityIncrements",
        "TreatmentCapacityIncrements",
        "TreatmentEfficiency",
        "DisposalExpansionCost",
        "StorageExpansionCost",
        "TreatmentExpansionCost",
        "PipelineCapexDistanceBased",
        "PipelineCapexCapacityBased",
        "PipelineCapacityIncrements",
        "PipelineExpansionDistance",
        "Hydraulics",
        "Economics",
        "PadWaterQuality",
        "StorageInitialWaterQuality",
        "PadStorageInitialWaterQuality",
    ]

    # note the double backslashes '\\' in that path reference
    with resources.path(
        "pareto.case_studies",
        "small_strategic_case_study.xlsx",
    ) as fpath:
        [df_sets, df_parameters] = get_data(fpath, set_list, parameter_list)

        # create mathematical model
        def _call_model_with_config(config_dict):
            reduced_strategic_model = create_model(df_sets, df_parameters, config_dict)
            return reduced_strategic_model

    return _call_model_with_config


@pytest.mark.unit
def test_basic_reduced_build_capex_capacity_based_capacity_calculated(
    build_reduced_strategic_model,
):
    """Make a model and make sure it doesn't throw exception"""
    m = build_reduced_strategic_model(
        config_dict={
            "objective": Objectives.cost,
            "pipeline_cost": PipelineCost.capacity_based,
            "pipeline_capacity": PipelineCapacity.calculated,
        }
    )
    assert degrees_of_freedom(m) == 63177
    # Check unit config arguments
    assert len(m.config) == 5
    assert m.config.objective
    assert isinstance(m.s_T, pyo.Set)
    assert isinstance(m.v_F_Piped, pyo.Var)
    assert isinstance(m.p_pi_Trucking, pyo.Param)
    assert isinstance(m.PipelineCapacityExpansion, pyo.Constraint)
    assert isinstance(m.PipelineExpansionCapEx, pyo.Constraint)


@pytest.mark.unit
def test_basic_reduced_build_capex_capacity_based_capacity_input(
    build_reduced_strategic_model,
):
    """Make a model and make sure it doesn't throw exception"""
    m = build_reduced_strategic_model(
        config_dict={
            "objective": Objectives.cost,
            "pipeline_cost": PipelineCost.capacity_based,
            "pipeline_capacity": PipelineCapacity.input,
        }
    )
    assert degrees_of_freedom(m) == 63177
    # Check unit config arguments
    assert len(m.config) == 5
    assert m.config.objective
    assert isinstance(m.s_T, pyo.Set)
    assert isinstance(m.v_F_Piped, pyo.Var)
    assert isinstance(m.p_pi_Trucking, pyo.Param)
    assert isinstance(m.PipelineCapacityExpansion, pyo.Constraint)
    assert isinstance(m.PipelineExpansionCapEx, pyo.Constraint)


@pytest.mark.unit
def test_basic_reduced_build_capex_distance_based_capacity_input(
    build_reduced_strategic_model,
):
    """Make a model and make sure it doesn't throw exception"""
    m = build_reduced_strategic_model(
        config_dict={
            "objective": Objectives.cost,
            "pipeline_cost": PipelineCost.distance_based,
            "pipeline_capacity": PipelineCapacity.input,
        }
    )
    assert degrees_of_freedom(m) == 63177
    # Check unit config arguments
    assert len(m.config) == 5
    assert m.config.objective
    assert isinstance(m.s_T, pyo.Set)
    assert isinstance(m.v_F_Piped, pyo.Var)
    assert isinstance(m.p_pi_Trucking, pyo.Param)
    assert isinstance(m.PipelineCapacityExpansion, pyo.Constraint)
    assert isinstance(m.PipelineExpansionCapEx, pyo.Constraint)


@pytest.mark.component
def test_strategic_model_scaling(build_reduced_strategic_model):
    m = build_reduced_strategic_model(
        config_dict={
            "objective": Objectives.cost,
            "pipeline_cost": PipelineCost.capacity_based,
            "pipeline_capacity": PipelineCapacity.input,
        }
    )
    scaled_m = scale_model(m, scaling_factor=100000)
    scaled_components = []
    scaled_vars = []
    unscaled_vars = []
    scaled_constraints = []
    unscaled_constraints = []
    [scaled_components.append(i.name) for i in scaled_m.scaling_factor.keys()]

    # Checking for scaled and unscaled variables
    for v in m.component_objects(ctype=pyo.Var):
        if "vb_y" not in v.name:
            if str("scaled_" + v.name) in scaled_components:
                scaled_vars.append(v.name)
            else:
                unscaled_vars.append(v.name)

    # Checking for scaled and unscaled constraints
    for c in m.component_objects(ctype=pyo.Constraint):
        if str("scaled_" + c.name) in scaled_components:
            scaled_constraints.append(c.name)
        else:
            unscaled_constraints.append(c.name)

    assert len(unscaled_vars) == 0
    assert len(unscaled_constraints) == 0


# if solver cbc exists @solver
@pytest.mark.component
def test_run_reduced_strategic_model(build_reduced_strategic_model):
    m = build_reduced_strategic_model(
        config_dict={
            "objective": Objectives.cost,
            "pipeline_cost": PipelineCost.distance_based,
            "pipeline_capacity": PipelineCapacity.input,
        }
    )

    options = {
        "deactivate_slacks": True,
        "scale_model": True,
        "scaling_factor": 1000,
        "running_time": 60 * 5,
        "gap": 0,
        "water_quality": False,
    }
    results = solve_model(model=m, options=options)

    assert results.solver.termination_condition == pyo.TerminationCondition.optimal
    assert results.solver.status == pyo.SolverStatus.ok
    assert degrees_of_freedom(m) == 61883
    # solutions obtained from running the reduced generic case study
    assert pytest.approx(10188.19, abs=1e-1) == pyo.value(m.v_Z)


@pytest.mark.component
def test_water_quality_reduced_strategic_model(build_reduced_strategic_model):
    m = build_reduced_strategic_model(
        config_dict={
            "objective": Objectives.cost,
            "pipeline_cost": PipelineCost.distance_based,
            "pipeline_capacity": PipelineCapacity.input,
        }
    )

    options = {
        "deactivate_slacks": True,
        "scale_model": True,
        "scaling_factor": 1000,
        "running_time": 60 * 5,
        "gap": 0,
        "water_quality": True,
    }
    results = solve_model(model=m, options=options)

    assert results.solver.termination_condition == pyo.TerminationCondition.optimal
    assert results.solver.status == pyo.SolverStatus.ok
    # solutions obtained from running the reduced generic case study water quality
    assert degrees_of_freedom(m) == -18826
    assert pytest.approx(9.06, abs=1e-1) == pyo.value(m.quality.v_X)
