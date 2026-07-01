"""
MockDataAgent: Generates realistic star schema and mock business datasets for Power BI dashboards.
"""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SchemaRelationship:
    """Represents a relationship between fact and dimension tables."""
    fact_table: str
    fact_column: str
    dimension_table: str
    dimension_column: str
    cardinality: str = "many-to-one"


@dataclass
class SchemaDefinition:
    """Internal schema definition before data generation."""
    fact_tables: List[str] = field(default_factory=list)
    dimension_tables: List[str] = field(default_factory=list)
    relationships: List[SchemaRelationship] = field(default_factory=list)
    grain: str = ""
    primary_keys: Dict[str, str] = field(default_factory=dict)
    foreign_keys: Dict[str, List[str]] = field(default_factory=dict)
    dimensions: Dict[str, List[str]] = field(default_factory=dict)  # dimension_name -> attributes
    measures: Dict[str, str] = field(default_factory=dict)  # measure_name -> datatype


@dataclass
class DataDictionaryEntry:
    """Metadata for a single column in the schema."""
    table: str
    column: str
    datatype: str
    description: str

from dataclasses import asdict

class MockDataAgent:
    """
    Agent responsible for generating realistic star schema datasets.
    
    Accepts RequirementContext and produces pandas DataFrames with mock business data,
    maintaining referential integrity and realistic values.
    """

    def __init__(self, requirement_context):
        """
        Initialize the MockDataAgent.
        
        Args:
            requirement_context: Dict containing dashboard requirements from RequirementAgent
        """
        if not isinstance(requirement_context, dict):
            requirement_context = asdict(requirement_context)
            
            
        self.requirement_context = requirement_context
        self.schema: Optional[SchemaDefinition] = None
        self.dataframes: Dict[str, pd.DataFrame] = {}
        self.data_dictionary: List[DataDictionaryEntry] = []
        logger.info("MockDataAgent initialized")

    def generate_mock_data(self) -> Dict[str, Any]:
        """
        Main orchestration method to generate complete star schema and mock data.
        
        Returns:
            Dictionary containing dataframes, metadata, and data dictionary
            
        Raises:
            ValueError: If schema validation fails
        """
        try:
            logger.info("Starting mock data generation")
            self.schema = self.build_star_schema()
            logger.info(f"Schema defined with {len(self.schema.fact_tables)} fact tables "
                       f"and {len(self.schema.dimension_tables)} dimension tables")
            
            self.generate_dimension_tables()
            self.generate_fact_tables()
            self.validate_schema()
            
            metadata = self.create_metadata()
            self.data_dictionary = self.create_data_dictionary()
            
            logger.info("Mock data generation completed successfully")
            
            return {
                "dataframes": self.dataframes,
                "metadata": metadata,
                "data_dictionary": self.data_dictionary
            }
        except Exception as e:
            logger.error(f"Error during mock data generation: {str(e)}")
            raise

    def build_star_schema(self) -> SchemaDefinition:
        """
        Dynamically build star schema from requirement context.
        Domain-agnostic: uses fact_tables, dimension_tables, relationships, dimensions, and measures.
        
        Returns:
            SchemaDefinition with fact/dimension tables and relationships
        """
        schema = SchemaDefinition()
        
        logger.info("Building domain-agnostic star schema from requirement context")
        
        # Extract schema definition from requirement context
        schema.fact_tables = self.requirement_context.get("fact_tables", [])
        schema.dimension_tables = self.requirement_context.get("dimension_tables", [])
        schema.grain = self.requirement_context.get("grain", "Atomic level")
        schema.dimensions = self.requirement_context.get("dimensions", [])
        schema.measures = self.requirement_context.get("measures", {})
        
        # Extract relationships from requirement context
        relationships_config = self.requirement_context.get("relationships", [])
        for rel in relationships_config:
            if isinstance(rel, dict):
                schema.relationships.append(
                    SchemaRelationship(
                        fact_table=rel.get("fact_table", ""),
                        fact_column=rel.get("fact_column", ""),
                        dimension_table=rel.get("dimension_table", ""),
                        dimension_column=rel.get("dimension_column", ""),
                        cardinality=rel.get("cardinality", "many-to-one")
                    )
                )
            elif isinstance(rel, SchemaRelationship):
                schema.relationships.append(rel)
        
        # Generate primary keys dynamically from context or use defaults
        schema.primary_keys = self._generate_primary_keys(schema)
        
        logger.info(f"Schema built with {len(schema.fact_tables)} fact table(s) "
                   f"and {len(schema.dimension_tables)} dimension table(s)")
        
        return schema
    
    def _generate_primary_keys(self, schema: SchemaDefinition) -> Dict[str, str]:
        """
        Generate primary key mappings for all tables.
        Uses context if available, otherwise generates sensible defaults.
        
        Args:
            schema: SchemaDefinition to analyze
            
        Returns:
            Dictionary mapping table names to primary key columns
        """
        primary_keys = {}
        
        # Check if primary keys provided in context
        context_pk = self.requirement_context.get("primary_keys", {})
        if context_pk:
            primary_keys.update(context_pk)
        
        # Generate for any missing tables
        for table in schema.fact_tables + schema.dimension_tables:
            if table not in primary_keys:
                # Default naming convention
                primary_keys[table] = self._generate_id_column_name(table)
        
        return primary_keys
    
    def _generate_id_column_name(self, table_name: str) -> str:
        """
        Generate an ID column name based on table name.
        Dim* tables -> DimID, Fact* tables -> FactID, custom tables -> {Table}ID
        
        Args:
            table_name: Table name
            
        Returns:
            Generated ID column name
        """
        if table_name.startswith("Dim"):
            return table_name + "ID"
        elif table_name.startswith("Fact"):
            return table_name.replace("Fact", "") + "ID"
        else:
            return table_name + "ID"



    def generate_dimension_tables(self) -> None:
        """Generate all dimension tables based on schema definition."""
        if not self.schema:
            raise ValueError("Schema not defined")
        
        logger.info(f"Generating {len(self.schema.dimension_tables)} dimension tables")
        
        for dim_table in self.schema.dimension_tables:
            # Check if custom data generator provided in context
            custom_generator = self._get_custom_dimension_generator(dim_table)
            if custom_generator:
                self.dataframes[dim_table] = custom_generator()
            else:
                # Generate generic dimension table based on schema definition
                self.dataframes[dim_table] = self._generate_generic_dimension(dim_table)
    
    def _get_custom_dimension_generator(self, dim_table: str) -> Optional[Any]:
        """
        Retrieve custom data generator for a dimension table if provided.
        
        Args:
            dim_table: Dimension table name
            
        Returns:
            Custom generator function or None
        """
        custom_generators = self.requirement_context.get("custom_dimension_generators", {})
        return custom_generators.get(dim_table)
    
    def _generate_generic_dimension(self, dim_table: str) -> pd.DataFrame:
        """
        Generate a generic dimension table based on schema definition.
        
        Args:
            dim_table: Dimension table name
            
        Returns:
            Generated dimension DataFrame
        """
        primary_key = self.schema.primary_keys.get(dim_table, "ID")
        
        # Get attributes from schema dimensions definition
        attributes = []

        if isinstance(self.schema.dimensions, dict):
            attributes = self.schema.dimensions.get(dim_table, [])

        elif isinstance(self.schema.dimensions, list):
            for item in self.schema.dimensions:
                if isinstance(item, dict) :
                    if item.get("name") == dim_table or item.get("table") == dim_table:
                        attributes = item.get("attributes", [])
                        break
        
        # Determine row count (default: 100)
        row_count = self._get_dimension_row_count(dim_table)
        
        data = {primary_key: range(1, row_count + 1)}
        
        # Generate columns for each attribute
        for attr in attributes:
            data[attr] = self._generate_attribute_values(attr, row_count)
        
        df = pd.DataFrame(data)
        logger.info(f"Generated {dim_table} with {len(df)} rows and {len(df.columns)} columns")
        return df
    
    def _get_dimension_row_count(self, dim_table: str) -> int:
        """
        Determine row count for dimension table from context or use default.
        
        Args:
            dim_table: Dimension table name
            
        Returns:
            Row count for the dimension
        """
        dimension_sizes = self.requirement_context.get("dimension_sizes", {})
        return dimension_sizes.get(dim_table, 100)
    
    def _generate_attribute_values(self, attribute: str, count: int) -> List[Any]:
        """
        Generate realistic values for a dimension attribute.
        
        Args:
            attribute: Attribute name
            count: Number of values to generate
            
        Returns:
            List of generated values
        """
        attr_lower = attribute.lower()
        
        # Date attributes
        if "date" in attr_lower or "datetime" in attr_lower:
            return [datetime(2022, 1, 1) + timedelta(days=int(x)) for x in np.random.uniform(0, 1095, count)]
        
        # ID attributes
        if "id" in attr_lower:
            return range(1, count + 1)
        
        # Boolean attributes
        if "is_" in attr_lower or "active" in attr_lower:
            return np.random.choice([True, False], count, p=[0.85, 0.15])
        
        # Name/String attributes
        if "name" in attr_lower or "title" in attr_lower or "description" in attr_lower:
            return [f"{attribute}_{i}" for i in range(1, count + 1)]
        
        # Email attributes
        if "email" in attr_lower:
            return [f"user{i}@example.com" for i in range(1, count + 1)]
        
        # Phone/Address attributes
        if "phone" in attr_lower:
            return [f"555-{np.random.randint(1000, 9999)}" for _ in range(count)]
        
        # Default: random strings
        return [f"{attribute}_{i}" for i in range(1, count + 1)]



    def generate_fact_tables(self) -> None:
        """Generate all fact tables based on schema definition."""
        if not self.schema:
            raise ValueError("Schema not defined")
        
        logger.info(f"Generating {len(self.schema.fact_tables)} fact tables")
        
        for fact_table in self.schema.fact_tables:
            # Check if custom data generator provided in context
            custom_generator = self._get_custom_fact_generator(fact_table)
            if custom_generator:
                self.dataframes[fact_table] = custom_generator()
            else:
                # Generate generic fact table based on schema definition
                self.dataframes[fact_table] = self._generate_generic_fact_table(fact_table)
    
    def _get_custom_fact_generator(self, fact_table: str) -> Optional[Any]:
        """
        Retrieve custom data generator for a fact table if provided.
        
        Args:
            fact_table: Fact table name
            
        Returns:
            Custom generator function or None
        """
        custom_generators = self.requirement_context.get("custom_fact_generators", {})
        return custom_generators.get(fact_table)
    
    def _generate_generic_fact_table(self, fact_table: str) -> pd.DataFrame:
        """
        Generate a generic fact table based on schema definition and relationships.
        
        Args:
            fact_table: Fact table name
            
        Returns:
            Generated fact DataFrame
        """
        primary_key = self.schema.primary_keys.get(fact_table, "ID")
        
        # Determine row count (default: 1000)
        fact_sizes = self.requirement_context.get("fact_table_sizes", {})
        row_count = fact_sizes.get(fact_table, 1000)
        
        data = {primary_key: range(1, row_count + 1)}
        
        # Add foreign key references from relationships
        for rel in self.schema.relationships:
            if rel.fact_table == fact_table:
                dim_df = self.dataframes.get(rel.dimension_table)
                if dim_df is not None and len(dim_df) > 0:
                    max_fk_value = len(dim_df)
                    data[rel.fact_column] = np.random.randint(1, max_fk_value + 1, row_count)
        
        # Add measures from schema
        if isinstance(self.schema.measures, dict):
            for measure_name, measure_type in self.schema.measures.items():
                if str(measure_type).lower() in ['integer', 'int', 'count', 'quantity']:
                    data[measure_name] = np.random.randint(1, 100, row_count)
                elif str(measure_type).lower() in ['decimal', 'float', 'amount', 'price']:
                    data[measure_name] = np.random.uniform(10, 500, row_count).round(2)
                else:
                    # Default to float
                    data[measure_name] = np.random.uniform(1, 100, row_count).round(2)
        
        df = pd.DataFrame(data)
        logger.info(f"Generated {fact_table} with {len(df)} rows and {len(df.columns)} columns")
        return df

    def validate_schema(self) -> None:
        """Validate schema integrity and referential constraints."""
        logger.info("Validating schema integrity and referential integrity")
        
        if not self.schema or not self.dataframes:
            raise ValueError("Schema or dataframes not initialized")
        
        validation_errors = []
        validation_warnings = []
        
        # Validate fact tables exist
        for fact_table in self.schema.fact_tables:
            if fact_table not in self.dataframes:
                validation_errors.append(f"Missing fact table: {fact_table}")
        
        # Validate dimension tables exist
        for dim_table in self.schema.dimension_tables:
            if dim_table not in self.dataframes:
                validation_errors.append(f"Missing dimension table: {dim_table}")
        
        # Validate relationships and referential integrity
        for relationship in self.schema.relationships:
            fact_df = self.dataframes.get(relationship.fact_table)
            dim_df = self.dataframes.get(relationship.dimension_table)
            
            if fact_df is None or dim_df is None:
                validation_warnings.append(
                    f"Missing dataframe for relationship: {relationship.fact_table} -> {relationship.dimension_table}"
                )
                continue
            
            # Check columns exist
            if relationship.fact_column not in fact_df.columns:
                validation_errors.append(
                    f"Foreign key column missing: {relationship.fact_table}.{relationship.fact_column}"
                )
                continue
            
            if relationship.dimension_column not in dim_df.columns:
                validation_errors.append(
                    f"Primary key column missing: {relationship.dimension_table}.{relationship.dimension_column}"
                )
                continue
            
            # Check for orphaned foreign keys
            fact_fk_values = set(fact_df[relationship.fact_column].unique())
            dim_pk_values = set(dim_df[relationship.dimension_column].unique())
            orphaned = fact_fk_values - dim_pk_values
            
            if len(orphaned) > 0:
                validation_warnings.append(
                    f"Orphaned FK values in {relationship.fact_table}.{relationship.fact_column}: {len(orphaned)} found"
                )
        
        # Log validation results
        if validation_errors:
            for error in validation_errors:
                logger.error(f"Validation error: {error}")
            raise ValueError(f"Schema validation failed with {len(validation_errors)} error(s)")
        
        for warning in validation_warnings:
            logger.warning(f"Validation warning: {warning}")
        
        logger.info("Schema validation completed successfully")

    def create_metadata(self) -> Dict[str, Any]:
        """Create metadata about the generated schema and data."""
        if not self.schema:
            raise ValueError("Schema not defined")
        
        row_counts = {table: len(df) for table, df in self.dataframes.items()}
        
        metadata = {
            "fact_tables": self.schema.fact_tables,
            "dimension_tables": self.schema.dimension_tables,
            "relationships": [
                {
                    "fact_table": r.fact_table,
                    "fact_column": r.fact_column,
                    "dimension_table": r.dimension_table,
                    "dimension_column": r.dimension_column,
                    "cardinality": r.cardinality
                }
                for r in self.schema.relationships
            ],
            "grain": self.schema.grain,
            "row_counts": row_counts,
            "primary_keys": self.schema.primary_keys
        }
        
        logger.info(f"Metadata created: {len(row_counts)} tables")
        return metadata

    def create_data_dictionary(self) -> List[DataDictionaryEntry]:
        """Create data dictionary with column metadata."""
        entries = []
        
        dtype_map = {
            'int64': 'Integer',
            'float64': 'Decimal',
            'object': 'String',
            'bool': 'Boolean',
            'datetime64[ns]': 'DateTime'
        }
        
        for table_name, df in self.dataframes.items():
            for col_name, dtype in df.dtypes.items():
                datatype = dtype_map.get(str(dtype), str(dtype))
                description = f"{col_name} in {table_name}"
                
                entries.append(DataDictionaryEntry(
                    table=table_name,
                    column=col_name,
                    datatype=datatype,
                    description=description
                ))
        
        logger.info(f"Created data dictionary with {len(entries)} entries")
        return entries


def create_mock_data_from_requirements(requirement_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convenience function to generate mock data from requirement context.
    
    Args:
        requirement_context: Dict from RequirementAgent
        
    Returns:
        Dictionary with dataframes, metadata, and data dictionary
    """
    agent = MockDataAgent(requirement_context)
    return agent.generate_mock_data()
