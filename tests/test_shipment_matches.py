import pytest
import uuid
from decimal import Decimal
from sqlalchemy.exc import IntegrityError
import models


class TestShipmentMatch:
    def test_create_shipment_match_happy_path(
        self, db_session, sample_shipment, sample_truck, sample_fleet_user
    ):
        match = models.ShipmentMatch(
            shipment_id=sample_shipment.shipment_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
            distance_km=500.0,
            duration=600,
            fuel_cost=1500.00,
            driver_cost=300.00,
            toll_cost=100.00,
            maintenance_cost=250.00,
            other_cost=50.00,
            estimated_total_cost=2200.00,
            proposed_amount=3000.00,
            estimated_margin=800.00,
            outcome=models.MatchOutcome.PROFIT,
            ai_explanation="The shipment is expected to be profitable.",
            manager_decision=models.ManagerDecision.PENDING,
        )
        db_session.add(match)
        db_session.commit()
        db_session.refresh(match)

        assert match.match_id is not None
        assert isinstance(match.match_id, uuid.UUID)
        assert match.shipment_id == sample_shipment.shipment_id
        assert match.truck_id == sample_truck.truck_id
        assert match.user_id == sample_fleet_user.user_id
        assert match.distance_km == 500.0
        assert match.duration == 600
        assert match.fuel_cost == Decimal("1500.00")
        assert match.driver_cost == Decimal("300.00")
        assert match.toll_cost == Decimal("100.00")
        assert match.maintenance_cost == Decimal("250.00")
        assert match.other_cost == Decimal("50.00")
        assert match.estimated_total_cost == Decimal("2200.00")
        assert match.proposed_amount == Decimal("3000.00")
        assert match.estimated_margin == Decimal("800.00")
        assert match.outcome == models.MatchOutcome.PROFIT
        assert match.ai_explanation == "The shipment is expected to be profitable."
        assert match.manager_decision == models.ManagerDecision.PENDING
        assert match.created_at is not None
        assert match.decided_at is None

    def test_shipment_match_optional_fields(
        self, db_session, sample_shipment, sample_truck
    ):
        match = models.ShipmentMatch(
            shipment_id=sample_shipment.shipment_id,
            truck_id=sample_truck.truck_id,
        )
        db_session.add(match)
        db_session.commit()
        db_session.refresh(match)

        assert match.user_id is None
        assert match.distance_km is None
        assert match.duration is None
        assert match.fuel_cost is None
        assert match.driver_cost is None
        assert match.toll_cost is None
        assert match.maintenance_cost is None
        assert match.other_cost is None
        assert match.estimated_total_cost is None
        assert match.proposed_amount is None
        assert match.estimated_margin is None
        assert match.outcome is None
        assert match.ai_explanation is None
        assert match.decided_at is None
        assert match.manager_decision == models.ManagerDecision.PENDING
        assert match.created_at is not None

    @pytest.mark.parametrize(
        "decision",
        [
            models.ManagerDecision.PENDING,
            models.ManagerDecision.ACCEPTED,
            models.ManagerDecision.DECLINED,
            models.ManagerDecision.CLOSED,
        ],
    )
    def test_shipment_match_manager_decision_values(
        self, db_session, sample_shipment, sample_truck, decision
    ):
        match = models.ShipmentMatch(
            shipment_id=sample_shipment.shipment_id,
            truck_id=sample_truck.truck_id,
            manager_decision=decision,
        )
        db_session.add(match)
        db_session.commit()
        db_session.refresh(match)

        assert match.manager_decision == decision

    @pytest.mark.parametrize(
        "outcome",
        [
            models.MatchOutcome.PROFIT,
            models.MatchOutcome.LOSS,
            models.MatchOutcome.BREAK_EVEN,
        ],
    )
    def test_shipment_match_outcome_values(
        self, db_session, sample_shipment, sample_truck, outcome
    ):
        match = models.ShipmentMatch(
            shipment_id=sample_shipment.shipment_id,
            truck_id=sample_truck.truck_id,
            outcome=outcome,
        )
        db_session.add(match)
        db_session.commit()
        db_session.refresh(match)

        assert match.outcome == outcome

    def test_shipment_match_missing_required_fields(self, db_session):
        match = models.ShipmentMatch()
        db_session.add(match)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_shipment_match_missing_shipment_id(self, db_session, sample_truck):
        match = models.ShipmentMatch(truck_id=sample_truck.truck_id)
        db_session.add(match)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_shipment_match_missing_truck_id(self, db_session, sample_shipment):
        match = models.ShipmentMatch(shipment_id=sample_shipment.shipment_id)
        db_session.add(match)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_shipment_match_unique_shipment_truck(
        self, db_session, sample_shipment, sample_truck
    ):
        match1 = models.ShipmentMatch(
            shipment_id=sample_shipment.shipment_id,
            truck_id=sample_truck.truck_id,
        )
        db_session.add(match1)
        db_session.commit()

        match2 = models.ShipmentMatch(
            shipment_id=sample_shipment.shipment_id,
            truck_id=sample_truck.truck_id,
        )
        db_session.add(match2)

        with pytest.raises(IntegrityError):
            db_session.commit()

        db_session.rollback()

    def test_shipment_match_shipment_relationship(
        self, db_session, sample_shipment, sample_truck
    ):
        match = models.ShipmentMatch(
            shipment_id=sample_shipment.shipment_id,
            truck_id=sample_truck.truck_id,
        )
        db_session.add(match)
        db_session.commit()
        db_session.refresh(match)

        assert match.shipment.shipment_id == sample_shipment.shipment_id
        assert match in sample_shipment.matches

    def test_shipment_match_truck_relationship(
        self, db_session, sample_shipment, sample_truck
    ):
        match = models.ShipmentMatch(
            shipment_id=sample_shipment.shipment_id,
            truck_id=sample_truck.truck_id,
        )
        db_session.add(match)
        db_session.commit()
        db_session.refresh(match)

        assert match.truck.truck_id == sample_truck.truck_id
        assert match in sample_truck.shipment_matches

    def test_shipment_match_user_relationship(
        self, db_session, sample_shipment, sample_truck, sample_fleet_user
    ):
        match = models.ShipmentMatch(
            shipment_id=sample_shipment.shipment_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
        )
        db_session.add(match)
        db_session.commit()
        db_session.refresh(match)

        assert match.user.user_id == sample_fleet_user.user_id
        assert match in sample_fleet_user.shipment_matches

    def test_shipment_match_reservation_relationship(
        self,
        db_session,
        sample_shipment,
        sample_match,
        sample_fleet_company,
        sample_truck,
        sample_fleet_user,
    ):
        reservation = models.Reservation(
            shipment_id=sample_shipment.shipment_id,
            company_id=sample_fleet_company.company_id,
            truck_id=sample_truck.truck_id,
            user_id=sample_fleet_user.user_id,
            match_id=sample_match.match_id,
        )
        db_session.add(reservation)
        db_session.commit()
        db_session.refresh(reservation)

        assert sample_match.reservation is not None
        assert sample_match.reservation.reservation_id == reservation.reservation_id
