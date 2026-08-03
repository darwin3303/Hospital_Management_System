"""Import every feature's models module here so Base.metadata is fully
populated for Alembic autogenerate and for create_all() in tests."""

from app.features.auth import models as auth_models          # noqa: F401
from app.features.staff import models as staff_models        # noqa: F401
from app.features.doctors import models as doctors_models    # noqa: F401
from app.features.patients import models as patients_models  # noqa: F401
from app.features.appointments import models as appointments_models  # noqa: F401
from app.features.emr import models as emr_models            # noqa: F401
from app.features.laboratory import models as laboratory_models  # noqa: F401
from app.features.pharmacy import models as pharmacy_models   # noqa: F401
from app.features.billing import models as billing_models     # noqa: F401
from app.features.inpatient import models as inpatient_models  # noqa: F401
from app.core import audit  # noqa: F401
