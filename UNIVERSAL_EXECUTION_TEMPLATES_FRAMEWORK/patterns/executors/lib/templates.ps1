#!/usr/bin/env pwsh
# DOC_LINK: DOC-PAT-TEMPLATES-1182
# DOC_LINK: DOC-PAT-TEMPLATES-974
# DOC_LINK: DOC-PAT-TEMPLATES-238
<#
.SYNOPSIS
    Shared template library for pattern executors

.DESCRIPTION
    Provides template loading, variable substitution, and validation for:
    - CRUD endpoints
    - Database models
    - Test files
    - Configuration files

.NOTES
    Module: templates.ps1
    Version: 1.0.0
    Requires: PowerShell 7+
    DOC_LINK: DOC-LIB-TEMPLATES-001
#>

#region Template Loading

function Load-Template {
    <#
    .SYNOPSIS
        Loads a template from built-in templates or custom path
    
    .PARAMETER TemplateName
        Name of built-in template (crud, model, test, config) or path to custom template
    
    .PARAMETER Language
        Programming language for the template
    
    .OUTPUTS
        Hashtable with template: @{ content=$string; variables=@(); metadata=@{} }
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$TemplateName,
        
        [Parameter(Mandatory=$false)]
        [string]$Language = "python"
    )
    
    $template = @{
        content = ""
        variables = @()
        metadata = @{}
    }
    
    # Check if it's a custom template path
    if (Test-Path $TemplateName) {
        $template.content = Get-Content $TemplateName -Raw
        $template.metadata.source = "custom"
        $template.metadata.path = $TemplateName
    }
    else {
        # Load built-in template
        $template.content = Get-BuiltInTemplate -TemplateName $TemplateName -Language $Language
        $template.metadata.source = "built-in"
        $template.metadata.name = $TemplateName
        $template.metadata.language = $Language
    }
    
    # Extract variables from template ({{variable_name}} format)
    $template.variables = [regex]::Matches($template.content, '\{\{(\w+)\}\}') | 
        ForEach-Object { $_.Groups[1].Value } | 
        Select-Object -Unique
    
    return $template
}

function Get-BuiltInTemplate {
    <#
    .SYNOPSIS
        Returns built-in template content
    
    .PARAMETER TemplateName
        Template name (crud, model, test, config)
    
    .PARAMETER Language
        Programming language
    
    .OUTPUTS
        String template content
    #>
    param(
        [string]$TemplateName,
        [string]$Language
    )
    
    $templates = @{
        "python" = @{
            "crud" = @"
"""{{description}}"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import {{entity}}Schema, {{entity}}Create, {{entity}}Update
from ..models import {{entity}}

router = APIRouter(prefix="/{{endpoint}}", tags=["{{tag}}"])


@router.get("/", response_model=List[{{entity}}Schema])
async def list_{{plural}}(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """List all {{plural}}"""
    items = db.query({{entity}}).offset(skip).limit(limit).all()
    return items


@router.post("/", response_model={{entity}}Schema, status_code=201)
async def create_{{singular}}(
    data: {{entity}}Create,
    db: Session = Depends(get_db)
):
    """Create a new {{singular}}"""
    item = {{entity}}(**data.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@router.get("/{item_id}", response_model={{entity}}Schema)
async def get_{{singular}}(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Get {{singular}} by ID"""
    item = db.query({{entity}}).filter({{entity}}.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="{{entity}} not found")
    return item


@router.put("/{item_id}", response_model={{entity}}Schema)
async def update_{{singular}}(
    item_id: int,
    data: {{entity}}Update,
    db: Session = Depends(get_db)
):
    """Update {{singular}} by ID"""
    item = db.query({{entity}}).filter({{entity}}.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="{{entity}} not found")
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(item, key, value)
    
    db.commit()
    db.refresh(item)
    return item


@router.delete("/{item_id}", status_code=204)
async def delete_{{singular}}(
    item_id: int,
    db: Session = Depends(get_db)
):
    """Delete {{singular}} by ID"""
    item = db.query({{entity}}).filter({{entity}}.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="{{entity}} not found")
    
    db.delete(item)
    db.commit()
"@
            "model" = @"
"""{{description}}"""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from datetime import datetime

from ..database import Base


class {{entity}}(Base):
    """{{entity}} database model"""
    __tablename__ = "{{table_name}}"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Add your fields here
    {{fields}}
    
    def __repr__(self):
        return f"<{{entity}}(id={self.id})>"
"@
            "test" = @"
"""{{description}}"""
import pytest
from {{module}} import {{function}}


def test_{{function}}_happy_path():
    """Test {{function}} with valid input"""
    result = {{function}}({{test_input}})
    assert result == {{expected_output}}


def test_{{function}}_edge_case_empty():
    """Test {{function}} with empty input"""
    result = {{function}}({{empty_input}})
    assert result == {{empty_output}}


def test_{{function}}_invalid_input():
    """Test {{function}} with invalid input"""
    with pytest.raises({{exception}}):
        {{function}}({{invalid_input}})


@pytest.mark.parametrize("input_val,expected", [
    {{parametrize_cases}}
])
def test_{{function}}_parametrized(input_val, expected):
    """Test {{function}} with multiple inputs"""
    result = {{function}}(input_val)
    assert result == expected
"@
            "config" = @"
"""{{description}}"""
from pydantic import BaseSettings, Field
from typing import Optional


class {{entity}}Config(BaseSettings):
    """{{entity}} configuration"""
    
    # Database
    database_url: str = Field(..., env="DATABASE_URL")
    
    # API
    api_host: str = Field("0.0.0.0", env="API_HOST")
    api_port: int = Field(8000, env="API_PORT")
    
    # Security
    secret_key: str = Field(..., env="SECRET_KEY")
    algorithm: str = Field("HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Logging
    log_level: str = Field("INFO", env="LOG_LEVEL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


config = {{entity}}Config()
"@
        }
        "javascript" = @{
            "test" = @"
/**
 * {{description}}
 */
import { {{function}} } from '{{module}}';

describe('{{function}}', () => {
  test('should handle valid input', () => {
    const result = {{function}}({{test_input}});
    expect(result).toBe({{expected_output}});
  });

  test('should handle empty input', () => {
    const result = {{function}}({{empty_input}});
    expect(result).toBe({{empty_output}});
  });

  test('should throw on invalid input', () => {
    expect(() => {{function}}({{invalid_input}})).toThrow({{exception}});
  });
});
"@
        }
    }
    
    if ($templates.ContainsKey($Language) -and $templates[$Language].ContainsKey($TemplateName)) {
        return $templates[$Language][$TemplateName]
    }
    else {
        throw "Template not found: $TemplateName for language $Language"
    }
}

#endregion

#region Variable Substitution

function Substitute-Variables {
    <#
    .SYNOPSIS
        Substitutes variables in template with provided values
    
    .PARAMETER TemplateContent
        Template string with {{variable}} placeholders
    
    .PARAMETER Variables
        Hashtable of variable values: @{ entity="User"; table_name="users" }
    
    .PARAMETER StrictMode
        If true, fails if any variables are missing
    
    .OUTPUTS
        String with substituted variables
    #>
    param(
        [Parameter(Mandatory=$true)]
        [string]$TemplateContent,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Variables,
        
        [Parameter(Mandatory=$false)]
        [switch]$StrictMode
    )
    
    $result = $TemplateContent
    
    # Find all variables in template
    $templateVars = [regex]::Matches($result, '\{\{(\w+)\}\}') | 
        ForEach-Object { $_.Groups[1].Value } | 
        Select-Object -Unique
    
    # Check for missing variables in strict mode
    if ($StrictMode) {
        $missing = $templateVars | Where-Object { -not $Variables.ContainsKey($_) }
        if ($missing.Count -gt 0) {
            throw "Missing required variables: $($missing -join ', ')"
        }
    }
    
    # Substitute each variable
    foreach ($var in $Variables.Keys) {
        $result = $result -replace "\{\{$var\}\}", $Variables[$var]
    }
    
    return $result
}

#endregion

#region Template Validation

function Validate-TemplateVars {
    <#
    .SYNOPSIS
        Validates that all template variables are provided
    
    .PARAMETER TemplateContent
        Template string or template object from Load-Template
    
    .PARAMETER Variables
        Hashtable of variable values
    
    .OUTPUTS
        Hashtable with validation results: @{ valid=$true; missing=@(); extra=@() }
    #>
    param(
        [Parameter(Mandatory=$true)]
        $TemplateContent,
        
        [Parameter(Mandatory=$true)]
        [hashtable]$Variables
    )
    
    $validation = @{
        valid = $true
        missing = @()
        extra = @()
        warnings = @()
    }
    
    # Extract template content if object was passed
    $content = if ($TemplateContent -is [hashtable] -and $TemplateContent.content) {
        $TemplateContent.content
    } else {
        $TemplateContent
    }
    
    # Find all variables in template
    $templateVars = [regex]::Matches($content, '\{\{(\w+)\}\}') | 
        ForEach-Object { $_.Groups[1].Value } | 
        Select-Object -Unique
    
    # Check for missing variables
    $validation.missing = $templateVars | Where-Object { -not $Variables.ContainsKey($_) }
    if ($validation.missing.Count -gt 0) {
        $validation.valid = $false
    }
    
    # Check for extra variables (not used in template)
    $validation.extra = $Variables.Keys | Where-Object { $_ -notin $templateVars }
    if ($validation.extra.Count -gt 0) {
        $validation.warnings += "Unused variables provided: $($validation.extra -join ', ')"
    }
    
    return $validation
}

#endregion

# Export functions
Export-ModuleMember -Function @(
    'Load-Template',
    'Substitute-Variables',
    'Validate-TemplateVars'
)
