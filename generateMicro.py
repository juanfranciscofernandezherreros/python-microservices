import os
import zipfile

# Función para generar el contenido del POM
def generate_pom_content(project_name):
    dependencies = [
        ("org.springframework.boot", "spring-boot-starter-web", "3.1.4"),
        ("org.springframework.boot", "spring-boot-starter-data-jpa", "3.1.4"),
        ("com.h2database", "h2", "2.1.214"),
        ("org.projectlombok", "lombok", "1.18.24"),
        ("org.mapstruct", "mapstruct", "1.5.3.Final"),
        ("org.mapstruct", "mapstruct-processor", "1.5.3.Final"),
        ("org.springdoc", "springdoc-openapi-starter-webmvc-ui", "2.1.0"),
        ("org.slf4j", "slf4j-api", "2.0.9"),
        ("ch.qos.logback", "logback-classic", "1.4.11"),
        ("jakarta.persistence", "jakarta.persistence-api", "3.0.0"),
        ("org.hibernate.orm", "hibernate-core", "6.1.0.Final")
    ]
    
    dependencies_str = "\n".join([f'''<dependency>
            <groupId>{group_id}</groupId>
            <artifactId>{artifact_id}</artifactId>
            <version>{version}</version>
        </dependency>''' for group_id, artifact_id, version in dependencies])
    
    pom_content = f'''<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://www.maven.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>

    <groupId>com.example</groupId>
    <artifactId>{project_name.lower()}</artifactId>
    <version>1.0-SNAPSHOT</version>

    <dependencies>
        {dependencies_str}
    </dependencies>

    <build>
        <plugins>
            <plugin>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-maven-plugin</artifactId>
            </plugin>
            <plugin>
                <groupId>org.apache.maven.plugins</groupId>
                <artifactId>maven-compiler-plugin</artifactId>
                <configuration>
                    <source>17</source>
                    <target>17</target>
                </configuration>
            </plugin>
        </plugins>
    </build>
</project>
'''
    return pom_content

# Función para generar el contenido de la entidad
def generate_entity_content(entity_name, table_name, attributes, project_name):
    attributes_str = "\n".join([f"    private {attr_type} {attr_name};" for attr_name, attr_type in attributes])
    entity_content = f'''package com.example.{project_name.lower()}.model;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "{table_name}")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class {entity_name} {{

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
{attributes_str}
}}
'''
    return entity_content

# Función para generar el DTO
def generate_dto_content(entity_name, attributes, project_name):
    attributes_str = "\n".join([f"    private {attr_type} {attr_name};" for attr_name, attr_type in attributes])
    dto_content = f'''package com.example.{project_name.lower()}.dto;

import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class {entity_name}DTO {{

{attributes_str}
}}
'''
    return dto_content

# Función para generar el GlobalExceptionHandler.java
def generate_global_exception_handler(project_name):
    content = f'''package com.example.{project_name.lower()}.exception;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.ControllerAdvice;
import org.springframework.web.bind.annotation.ExceptionHandler;

@ControllerAdvice
public class GlobalExceptionHandler {{

    @ExceptionHandler(NotFoundException.class)
    public ResponseEntity<String> handleNotFoundException(NotFoundException ex) {{
        return ResponseEntity.status(HttpStatus.NOT_FOUND).body(ex.getMessage());
    }}

    @ExceptionHandler(AlreadyExistsException.class)
    public ResponseEntity<String> handleAlreadyExistsException(AlreadyExistsException ex) {{
        return ResponseEntity.status(HttpStatus.CONFLICT).body(ex.getMessage());
    }}

    @ExceptionHandler(Exception.class)
    public ResponseEntity<String> handleInternalServerError(Exception ex) {{
        return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body("Error interno del servidor: " + ex.getMessage());
    }}
}}
'''
    return content

# Función para generar NotFoundException.java y AlreadyExistsException.java
def generate_exception_classes(project_name):
    not_found_exception = f'''package com.example.{project_name.lower()}.exception;

public class NotFoundException extends RuntimeException {{
    public NotFoundException(String message) {{
        super(message);
    }}
}}
'''
    already_exists_exception = f'''package com.example.{project_name.lower()}.exception;

public class AlreadyExistsException extends RuntimeException {{
    public AlreadyExistsException(String message) {{
        super(message);
    }}
}}
'''
    return not_found_exception, already_exists_exception

# Función para generar el contenido de ResultadoSpecifications.java
def generate_specification_content(project_name):
    return f'''package com.example.{project_name.lower()}.specification;

import com.example.{project_name.lower()}.model.Resultado;
import jakarta.persistence.criteria.Predicate;
import org.springframework.data.jpa.domain.Specification;
import java.util.ArrayList;
import java.util.List;

public class ResultadoSpecifications {{

    public static Specification<Resultado> buildSpecifications(SearchCriteria[] searchCriteria) {{
        return (root, query, criteriaBuilder) -> {{
            List<Predicate> predicates = new ArrayList<>();
            for (SearchCriteria criteria : searchCriteria) {{
                switch (criteria.getOperation()) {{
                    case "eq":
                        predicates.add(criteriaBuilder.equal(root.get(criteria.getKey()), criteria.getValue()));
                        break;
                    case "neq":
                        predicates.add(criteriaBuilder.notEqual(root.get(criteria.getKey()), criteria.getValue()));
                        break;
                    case "like":
                        predicates.add(criteriaBuilder.like(root.get(criteria.getKey()), "%" + criteria.getValue() + "%"));
                        break;
                    case "lt":
                        predicates.add(criteriaBuilder.lessThan(root.get(criteria.getKey()), criteria.getValue().toString()));
                        break;
                    case "lte":
                        predicates.add(criteriaBuilder.lessThanOrEqualTo(root.get(criteria.getKey()), criteria.getValue().toString()));
                        break;
                    case "gt":
                        predicates.add(criteriaBuilder.greaterThan(root.get(criteria.getKey()), criteria.getValue().toString()));
                        break;
                    case "gte":
                        predicates.add(criteriaBuilder.greaterThanOrEqualTo(root.get(criteria.getKey()), criteria.getValue().toString()));
                        break;
                }}
            }}
            return criteriaBuilder.and(predicates.toArray(new Predicate[0]));
        }};
    }}
}}
'''

# Función para generar el contenido de SearchCriteria.java
def generate_search_criteria_content(project_name):
    return f'''package com.example.{project_name.lower()}.specification;

public class SearchCriteria {{

    private String key;
    private String operation;
    private Object value;

    public SearchCriteria() {{
    }}

    public SearchCriteria(String key, String operation, Object value) {{
        this.key = key;
        this.operation = operation;
        this.value = value;
    }}

    public String getKey() {{
        return key;
    }}

    public void setKey(String key) {{
        this.key = key;
    }}

    public String getOperation() {{
        return operation;
    }}

    public void setOperation(String operation) {{
        this.operation = operation;
    }}

    public Object getValue() {{
        return value;
    }}

    public void setValue(Object value) {{
        this.value = value;
    }}
}}
'''

# Función para generar el contenido del ResultadoService.java
def generate_service_content(entity_name, project_name):
    return f'''package com.example.{project_name.lower()}.service;

import com.example.{project_name.lower()}.dto.{entity_name}DTO;
import com.example.{project_name.lower()}.exception.AlreadyExistsException;
import com.example.{project_name.lower()}.exception.NotFoundException;
import com.example.{project_name.lower()}.model.{entity_name};
import com.example.{project_name.lower()}.repository.{entity_name}Repository;
import com.example.{project_name.lower()}.specification.ResultadoSpecifications;
import com.example.{project_name.lower()}.specification.SearchCriteria;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.*;
import org.springframework.stereotype.Service;

@Service
public class {entity_name}Service {{

    private final {entity_name}Repository {entity_name.lower()}Repository;

    @Autowired
    public {entity_name}Service({entity_name}Repository {entity_name.lower()}Repository) {{
        this.{entity_name.lower()}Repository = {entity_name.lower()}Repository;
    }}

    public {entity_name}DTO create{entity_name}({entity_name}DTO dto) {{
        if ({entity_name.lower()}Repository.existsById(dto.getId())) {{
            throw new AlreadyExistsException("El {entity_name.lower()} con el ID proporcionado ya existe.");
        }}
        {entity_name} entity = new {entity_name}(dto);
        {entity_name.lower()}Repository.save(entity);
        return new {entity_name}DTO(entity);
    }}

    public {entity_name}DTO get{entity_name}ById(String id) {{
        return {entity_name.lower()}Repository.findById(id)
                .map({entity_name}DTO::new)
                .orElseThrow(() -> new NotFoundException("{entity_name} no encontrado"));
    }}

    public {entity_name}DTO update{entity_name}(String id, {entity_name}DTO dto) {{
        {entity_name} entity = {entity_name.lower()}Repository.findById(id)
                .orElseThrow(() -> new NotFoundException("{entity_name} no encontrado"));
        entity.updateFromDTO(dto);
        {entity_name.lower()}Repository.save(entity);
        return new {entity_name}DTO(entity);
    }}

    public void delete{entity_name}(String id) {{
        if (!{entity_name.lower()}Repository.existsById(id)) {{
            throw new NotFoundException("{entity_name} no encontrado");
        }}
        {entity_name.lower()}Repository.deleteById(id);
    }}

    public Page<{entity_name}DTO> search{entity_name}s(SearchCriteria[] searchCriteria, int page, int size) {{
        Pageable pageable = PageRequest.of(page, size);
        Specification<{entity_name}> spec = ResultadoSpecifications.buildSpecifications(searchCriteria);
        return {entity_name.lower()}Repository.findAll(spec, pageable)
                .map({entity_name}DTO::new);
    }}
}}
'''

# Función para generar el contenido del ResultadoController.java
def generate_controller_content(entity_name, project_name):
    return f'''package com.example.{project_name.lower()}.controller;

import com.example.{project_name.lower()}.dto.{entity_name}DTO;
import com.example.{project_name.lower()}.service.{entity_name}Service;
import com.example.{project_name.lower()}.specification.SearchCriteria;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.*;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/{entity_name.lower()}s")
public class {entity_name}Controller {{

    private final {entity_name}Service {entity_name.lower()}Service;

    @Autowired
    public {entity_name}Controller({entity_name}Service {entity_name.lower()}Service) {{
        this.{entity_name.lower()}Service = {entity_name.lower()}Service;
    }}

    @PostMapping
    public ResponseEntity<{entity_name}DTO> create{entity_name}(@RequestBody {entity_name}DTO dto) {{
        {entity_name}DTO created = {entity_name.lower()}Service.create{entity_name}(dto);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }}

    @GetMapping("/{id}")
    public ResponseEntity<{entity_name}DTO> get{entity_name}ById(@PathVariable String id) {{
        return ResponseEntity.ok({entity_name.lower()}Service.get{entity_name}ById(id));
    }}

    @PutMapping("/{id}")
    public ResponseEntity<{entity_name}DTO> update{entity_name}(@PathVariable String id, @RequestBody {entity_name}DTO dto) {{
        return ResponseEntity.ok({entity_name.lower()}Service.update{entity_name}(id, dto));
    }}

    @DeleteMapping("/{id}")
    public ResponseEntity<Void> delete{entity_name}(@PathVariable String id) {{
        {entity_name.lower()}Service.delete{entity_name}(id);
        return ResponseEntity.noContent().build();
    }}

    @PostMapping("/search")
    public ResponseEntity<Page<{entity_name}DTO>> search{entity_name}s(@RequestBody SearchCriteria[] searchCriteria,
                                                                   @RequestParam(defaultValue = "0") int page,
                                                                   @RequestParam(defaultValue = "10") int size) {{
        Page<{entity_name}DTO> results = {entity_name.lower()}Service.search{entity_name}s(searchCriteria, page, size);
        return ResponseEntity.ok(results);
    }}
}}
'''

# Generar el proyecto completo
def generate_project():
    project_name = "resultado"
    entity_name = "Resultado"
    table_name = "resultados"
    attributes = [("id", "String"), ("name", "String"), ("score", "Integer")]

    # Crear estructura de carpetas base
    base_dir = f"/mnt/data/{project_name}"
    src_main_java = os.path.join(base_dir, "src", "main", "java", "com", "example", project_name)
    src_main_resources = os.path.join(base_dir, "src", "main", "resources")
    os.makedirs(src_main_java, exist_ok=True)
    os.makedirs(src_main_resources, exist_ok=True)

    # Crear los packages necesarios para las capas
    packages = {
        "controller": os.path.join(src_main_java, "controller"),
        "service": os.path.join(src_main_java, "service"),
        "repository": os.path.join(src_main_java, "repository"),
        "model": os.path.join(src_main_java, "model"),
        "dto": os.path.join(src_main_java, "dto"),
        "exception": os.path.join(src_main_java, "exception"),
        "specification": os.path.join(src_main_java, "specification"),
    }

    # Crear carpetas
    for package_path in packages.values():
        os.makedirs(package_path, exist_ok=True)

    # Generar y guardar las clases necesarias
    entity_content = generate_entity_content(entity_name, table_name, attributes, project_name)
    with open(os.path.join(packages["model"], f"{entity_name}.java"), "w") as f:
        f.write(entity_content)

    dto_content = generate_dto_content(entity_name, attributes, project_name)
    with open(os.path.join(packages["dto"], f"{entity_name}DTO.java"), "w") as f:
        f.write(dto_content)

    global_exception_handler_content = generate_global_exception_handler(project_name)
    with open(os.path.join(packages["exception"], "GlobalExceptionHandler.java"), "w") as f:
        f.write(global_exception_handler_content)

    not_found_exception_content, already_exists_exception_content = generate_exception_classes(project_name)
    with open(os.path.join(packages["exception"], "NotFoundException.java"), "w") as f:
        f.write(not_found_exception_content)
    with open(os.path.join(packages["exception"], "AlreadyExistsException.java"), "w") as f:
        f.write(already_exists_exception_content)

    # Generar y guardar SearchCriteria.java y ResultadoSpecifications.java
    search_criteria_content = generate_search_criteria_content(project_name)
    with open(os.path.join(packages["specification"], "SearchCriteria.java"), "w") as f:
        f.write(search_criteria_content)

    resultado_specifications_content = generate_specification_content(project_name)
    with open(os.path.join(packages["specification"], "ResultadoSpecifications.java"), "w") as f:
        f.write(resultado_specifications_content)

    # Generar y guardar el servicio y controlador
    service_content = generate_service_content(entity_name, project_name)
    with open(os.path.join(packages["service"], f"{entity_name}Service.java"), "w") as f:
        f.write(service_content)

    controller_content = generate_controller_content(entity_name, project_name)
    with open(os.path.join(packages["controller"], f"{entity_name}Controller.java"), "w") as f:
        f.write(controller_content)

    # Generar el archivo pom.xml
    pom_content = generate_pom_content(project_name)
    with open(os.path.join(base_dir, "pom.xml"), "w") as f:
        f.write(pom_content)

    # Generar archivo application.yml
    application_yml_content = '''server:
  port: 8080

spring:
  datasource:
    url: jdbc:h2:mem:testdb
    driverClassName: org.h2.Driver
    username: sa
    password: password
  h2:
    console:
      enabled: true
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true

logging:
  level:
    org.springframework: INFO
    com.example: DEBUG
'''
    with open(os.path.join(src_main_resources, "application.yml"), "w") as f:
        f.write(application_yml_content)

    # Crear un archivo zip con el proyecto completo
    zip_file_path_final = f"/mnt/data/{project_name}_final_complete.zip"
    with zipfile.ZipFile(zip_file_path_final, 'w') as zipf:
        for root, dirs, files in os.walk(base_dir):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file), base_dir))

    print(f"Proyecto generado con éxito: {zip_file_path_final}")

# Ejecutar el script
if __name__ == "__main__":
    generate_project()
