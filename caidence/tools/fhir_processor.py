"""
FHIR Resource Processor for cAIdence.

This module provides tools for processing FHIR (Fast Healthcare Interoperability Resources)
data alongside clinical text analysis.
"""

from typing import Dict, List, Any, Optional
import json
import logging
from datetime import datetime
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class FHIRResource:
    """Represents a FHIR resource with metadata."""
    resource_type: str
    id: str
    data: Dict[str, Any]
    last_updated: datetime
    version: str = "4.0.1"


class FHIRProcessor:
    """Processes FHIR resources for clinical analysis."""
    
    def __init__(self, base_url: Optional[str] = None):
        """Initialize FHIR processor.
        
        Args:
            base_url: Optional FHIR server base URL for remote operations
        """
        self.base_url = base_url
        self.supported_resources = {
            "Patient", "Observation", "Condition", "Procedure", 
            "MedicationRequest", "DiagnosticReport", "Encounter",
            "DocumentReference", "Practitioner", "Organization"
        }
    
    def extract_text_from_resource(self, resource: FHIRResource) -> List[str]:
        """Extract text content from FHIR resource.
        
        Args:
            resource: FHIR resource to process
            
        Returns:
            List of text strings extracted from the resource
        """
        texts = []
        
        try:
            if resource.resource_type == "DocumentReference":
                texts.extend(self._extract_from_document_reference(resource.data))
            elif resource.resource_type == "DiagnosticReport":
                texts.extend(self._extract_from_diagnostic_report(resource.data))
            elif resource.resource_type == "Observation":
                texts.extend(self._extract_from_observation(resource.data))
            elif resource.resource_type == "Condition":
                texts.extend(self._extract_from_condition(resource.data))
            elif resource.resource_type == "Procedure":
                texts.extend(self._extract_from_procedure(resource.data))
            else:
                logger.warning(f"Text extraction not implemented for {resource.resource_type}")
                
        except Exception as e:
            logger.error(f"Error extracting text from {resource.resource_type}: {str(e)}")
            
        return texts
    
    def _extract_from_document_reference(self, data: Dict[str, Any]) -> List[str]:
        """Extract text from DocumentReference resource."""
        texts = []
        
        # Extract from content
        if "content" in data:
            for content in data["content"]:
                if "attachment" in content:
                    attachment = content["attachment"]
                    if "data" in attachment:
                        # Base64 encoded content
                        texts.append(f"Document content: {attachment.get('title', 'Untitled')}")
                    if "url" in attachment:
                        texts.append(f"Document URL: {attachment['url']}")
        
        # Extract description
        if "description" in data:
            texts.append(data["description"])
            
        return texts
    
    def _extract_from_diagnostic_report(self, data: Dict[str, Any]) -> List[str]:
        """Extract text from DiagnosticReport resource."""
        texts = []
        
        # Extract conclusion
        if "conclusion" in data:
            texts.append(data["conclusion"])
            
        # Extract presentedForm text
        if "presentedForm" in data:
            for form in data["presentedForm"]:
                if "data" in form:
                    texts.append(f"Report form: {form.get('title', 'Report')}")
                    
        return texts
    
    def _extract_from_observation(self, data: Dict[str, Any]) -> List[str]:
        """Extract text from Observation resource."""
        texts = []
        
        # Extract value string
        if "valueString" in data:
            texts.append(data["valueString"])
            
        # Extract interpretation
        if "interpretation" in data:
            for interpretation in data["interpretation"]:
                if "text" in interpretation:
                    texts.append(interpretation["text"])
                    
        # Extract note
        if "note" in data:
            for note in data["note"]:
                if "text" in note:
                    texts.append(note["text"])
                    
        return texts
    
    def _extract_from_condition(self, data: Dict[str, Any]) -> List[str]:
        """Extract text from Condition resource."""
        texts = []
        
        # Extract code display
        if "code" in data and "text" in data["code"]:
            texts.append(data["code"]["text"])
            
        # Extract note
        if "note" in data:
            for note in data["note"]:
                if "text" in note:
                    texts.append(note["text"])
                    
        return texts
    
    def _extract_from_procedure(self, data: Dict[str, Any]) -> List[str]:
        """Extract text from Procedure resource."""
        texts = []
        
        # Extract code display
        if "code" in data and "text" in data["code"]:
            texts.append(data["code"]["text"])
            
        # Extract note
        if "note" in data:
            for note in data["note"]:
                if "text" in note:
                    texts.append(note["text"])
                    
        # Extract outcome
        if "outcome" in data and "text" in data["outcome"]:
            texts.append(data["outcome"]["text"])
            
        return texts
    
    def link_resources_to_patient(self, patient_id: str, resources: List[FHIRResource]) -> Dict[str, List[FHIRResource]]:
        """Link FHIR resources to a specific patient.
        
        Args:
            patient_id: Patient identifier
            resources: List of FHIR resources
            
        Returns:
            Dictionary mapping resource types to lists of related resources
        """
        linked_resources = {}
        
        for resource in resources:
            # Check if resource references the patient
            if self._resource_references_patient(resource, patient_id):
                resource_type = resource.resource_type
                if resource_type not in linked_resources:
                    linked_resources[resource_type] = []
                linked_resources[resource_type].append(resource)
                
        return linked_resources
    
    def _resource_references_patient(self, resource: FHIRResource, patient_id: str) -> bool:
        """Check if a resource references a specific patient."""
        data = resource.data
        
        # Direct patient reference
        if "subject" in data:
            if isinstance(data["subject"], dict) and "reference" in data["subject"]:
                return f"Patient/{patient_id}" in data["subject"]["reference"]
                
        # Patient resource itself
        if resource.resource_type == "Patient" and resource.id == patient_id:
            return True
            
        # Encounter reference (which links to patient)
        if "encounter" in data:
            # Would need to resolve encounter to patient - simplified for now
            return True
            
        return False
    
    def create_patient_timeline(self, patient_id: str, resources: List[FHIRResource]) -> List[Dict[str, Any]]:
        """Create a timeline of events for a patient.
        
        Args:
            patient_id: Patient identifier
            resources: List of FHIR resources
            
        Returns:
            Chronologically ordered list of patient events
        """
        timeline = []
        linked_resources = self.link_resources_to_patient(patient_id, resources)
        
        for resource_type, resource_list in linked_resources.items():
            for resource in resource_list:
                event = self._extract_timeline_event(resource)
                if event:
                    timeline.append(event)
        
        # Sort by date
        timeline.sort(key=lambda x: x.get("date", datetime.min))
        
        return timeline
    
    def _extract_timeline_event(self, resource: FHIRResource) -> Optional[Dict[str, Any]]:
        """Extract timeline event from FHIR resource."""
        data = resource.data
        event = {
            "resource_type": resource.resource_type,
            "id": resource.id,
            "date": None,
            "description": "",
            "category": resource.resource_type.lower()
        }
        
        # Extract date based on resource type
        date_fields = ["effectiveDateTime", "performedDateTime", "recordedDate", "date", "authoredOn"]
        for field in date_fields:
            if field in data:
                try:
                    event["date"] = datetime.fromisoformat(data[field].replace("Z", "+00:00"))
                    break
                except (ValueError, AttributeError):
                    continue
        
        # Extract description based on resource type
        if resource.resource_type == "Condition":
            if "code" in data and "text" in data["code"]:
                event["description"] = f"Condition: {data['code']['text']}"
        elif resource.resource_type == "Procedure":
            if "code" in data and "text" in data["code"]:
                event["description"] = f"Procedure: {data['code']['text']}"
        elif resource.resource_type == "Observation":
            if "code" in data and "text" in data["code"]:
                event["description"] = f"Observation: {data['code']['text']}"
        
        return event if event["date"] else None


def load_fhir_bundle(file_path: str) -> List[FHIRResource]:
    """Load FHIR resources from a bundle file.
    
    Args:
        file_path: Path to FHIR bundle JSON file
        
    Returns:
        List of FHIR resources
    """
    resources = []
    
    try:
        with open(file_path, 'r') as f:
            bundle = json.load(f)
            
        if "entry" in bundle:
            for entry in bundle["entry"]:
                if "resource" in entry:
                    resource_data = entry["resource"]
                    resource = FHIRResource(
                        resource_type=resource_data.get("resourceType", "Unknown"),
                        id=resource_data.get("id", "unknown"),
                        data=resource_data,
                        last_updated=datetime.now()
                    )
                    resources.append(resource)
                    
    except Exception as e:
        logger.error(f"Error loading FHIR bundle from {file_path}: {str(e)}")
        
    return resources
