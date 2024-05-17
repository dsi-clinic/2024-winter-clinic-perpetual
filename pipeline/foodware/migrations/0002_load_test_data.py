# Generated by Django 5.0.3 on 2024-03-12 01:15

# Standard library imports
import json

# Third-party imports
from django.db import migrations
from django.conf import settings
from django.contrib.gis.geos import GEOSGeometry
from shapely.geometry import MultiPolygon, Polygon, shape

# Application imports
from common.storage import IDataStoreFactory


def callback(apps, schema_editor):
    """Loads city boundaries into the database for testing."""

    # Initialize data store
    storage = IDataStoreFactory.get()

    # Fetch Django model
    django_model = apps.get_model("foodware", "FoodwareModel")

    # Process all test boundary files
    for fname in storage.list_contents(settings.TEST_BOUNDARIES_DIR):

        # Initialize model name and absolute file path to boundary
        name = f"test_{fname.split('.')[0]}"
        pth = f"{settings.TEST_BOUNDARIES_DIR}/{fname}"

        # If city already exists in database, skip to next
        try:
            django_model = django_model.objects.get(name=name)
            continue
        except django_model.DoesNotExist:
            pass

        # Otherwise, attempt to load city boundary from file and parse as JSON
        try:
            with storage.open_file(pth) as f:
                data = json.load(f)
        except FileNotFoundError:
            raise RuntimeError(
                f"POI fetch failed. Could not resolve the file path "
                f'"{pth}" to find the file in the configured data directory.'
            ) from None
        except json.JSONDecodeError as e:
            raise RuntimeError(
                f'POI fetch failed. Input boundary file "{pth}" '
                f"contains invalid JSON that cannot be processed. {e}"
            ) from None

        # Extract GeoJSON geometry and convert to Shapely MultiPolygon
        try:
            geometry = data["features"][0]["geometry"]
            polygon = shape(geometry)
            multi_polygon = (
                MultiPolygon([polygon]) if isinstance(polygon, Polygon) else polygon
            )
        except (KeyError, IndexError, AttributeError):
            raise RuntimeError(
                "POI fetch failed. The input boundary is not valid GeoJSON."
            ) from None

        # Load model with boundary into database
        django_model.objects.create(name=name, boundary=GEOSGeometry(multi_polygon.wkt))


class Migration(migrations.Migration):

    dependencies = [
        ("foodware", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(callback),
    ]