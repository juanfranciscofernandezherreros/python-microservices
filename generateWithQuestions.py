import os
import zipfile

# Función para preguntar si usar base de datos H2
def ask_database():
    use_h2 = input("¿Deseas usar H2 como base de datos? (S/n, por defecto 'S'): ").strip().lower() or "s"
    return use_h2 == "s"

# Función para preguntar las dependencias
def ask_dependencies():
    dependencies = []
    default_dependencies = [
        ("org.springframework.boot", "spring-boot-starter-web", "3.1.4"),
        ("org.springframework.boot", "spring-boot-starter-data-jpa", "3.1.4"),
        ("org.projectlombok", "lombok", "1.18.24", "provided"),
        ("org.mapstruct", "mapstruct", "1.5.3.Final"),
        ("org.mapstruct", "mapstruct-processor", "1.5.3.Final", "provided"),
        ("org.springdoc", "springdoc-openapi-starter-webmvc-ui", "2.1.0")
    ]
    for group_id, artifact_id, version, *scope in default_dependencies:
        include = input(f"¿Deseas incluir la dependencia {artifact_id}? (S/n, por defecto 'S'): ").strip().lower() or "s"
        if include == "s":
            dependencies.append((group_id, artifact_id, version, scope[0] if scope else None))
    
    return dependencies

# Función para generar el contenido del POM
def generate_pom_content(project_name, dependencies, use_h2):
    if use_h2:
        dependencies.append(("com.h2database", "h2", "2.1.214", "runtime"))
    
    dependencies_str = "\n".join([f'''<dependency>
            <groupId>{group_id}</groupId>
            <artifactId>{artifact_id}</artifactId>
            <version>{version}</version>
            {"<scope>" + scope + "</scope>" if scope else ""}
        </dependency>''' for group_id, artifact_id, version, scope in dependencies])
    
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

# Función para preguntar los atributos de la entidad y si son clave primaria
def ask_attributes():
    attributes = []
    while True:
        attr_name = input(f"Introduce el nombre del atributo (o presiona Enter para finalizar, valor por defecto 'id'): ").strip() or "id"
        attr_type = input(f"Introduce el tipo del atributo {attr_name} (valor por defecto 'String'): ").strip() or "String"
        
        # Preguntar si este atributo es clave primaria
        is_pk = input(f"¿Es el atributo {attr_name} una clave primaria? (S/n, por defecto 'n'): ").strip().lower() or "n"
        attributes.append((attr_name, attr_type, is_pk == 's'))
        
        another = input("¿Deseas añadir otro atributo? (S/n): ").strip().lower() or "s"
        if another == "n":
            break
    return attributes


# Función para preguntar si incluir cada endpoint
def ask_endpoints():
    endpoints = {
        "create": input("¿Deseas incluir el endpoint de creación? (S/n, por defecto 'S'): ").strip().lower() or "s",
        "get_by_id": input("¿Deseas incluir el endpoint de obtención por ID? (S/n, por defecto 'S'): ").strip().lower() or "s",
        "update": input("¿Deseas incluir el endpoint de actualización? (S/n, por defecto 'S'): ").strip().lower() or "s",
        "delete": input("¿Deseas incluir el endpoint de eliminación? (S/n, por defecto 'S'): ").strip().lower() or "s",
        "search": input("¿Deseas incluir el endpoint de búsqueda? (S/n, por defecto 'S'): ").strip().lower() or "s",
    }
    return {key: value == "s" for key, value in endpoints.items()}

# Función para generar el contenido del controlador basado en los endpoints seleccionados
def generate_controller_content(entity_name, project_name, endpoints):
    methods = []
    if endpoints["create"]:
        methods.append(f'''
    @PostMapping
    public ResponseEntity<{entity_name}DTO> create{entity_name}(@RequestBody {entity_name}DTO dto) {{
        {entity_name}DTO created = {entity_name.lower()}Service.create{entity_name}(dto);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }}
''')
    if endpoints["get_by_id"]:
        methods.append(f'''
    @GetMapping("/{{id}}")
    public ResponseEntity<{entity_name}DTO> get{entity_name}ById(@PathVariable String id) {{
        return ResponseEntity.ok({entity_name.lower()}Service.get{entity_name}ById(id));
    }}
''')
    if endpoints["update"]:
        methods.append(f'''
    @PutMapping("/{{id}}")
    public ResponseEntity<{entity_name}DTO> update{entity_name}(@PathVariable String id, @RequestBody {entity_name}DTO dto) {{
        return ResponseEntity.ok({entity_name.lower()}Service.update{entity_name}(id, dto));
    }}
''')
    if endpoints["delete"]:
        methods.append(f'''
    @DeleteMapping("/{{id}}")
    public ResponseEntity<Void> delete{entity_name}(@PathVariable String id) {{
        {entity_name.lower()}Service.delete{entity_name}(id);
        return ResponseEntity.noContent().build();
    }}
''')
    if endpoints["search"]:
        methods.append(f'''
    @PostMapping("/search")
    public ResponseEntity<Page<{entity_name}DTO>> search{entity_name}s(@RequestBody SearchCriteria[] searchCriteria,
                                                               @RequestParam(defaultValue = "0") int page,
                                                               @RequestParam(defaultValue = "10") int size) {{
        Page<{entity_name}DTO> results = {entity_name.lower()}Service.search{entity_name}s(searchCriteria, page, size);
        return ResponseEntity.ok(results);
    }}
''')

    controller_content = f'''package com.example.{project_name.lower()}.controller;

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
    
    {"".join(methods)}
}}
'''

    # Remplazar "{id}" por {{id}} en las rutas de @GetMapping, @PutMapping, @DeleteMapping
    return controller_content


# Función para generar el contenido del servicio
def generate_service_content(entity_name, project_name):
    service_content = f'''package com.example.{project_name.lower()}.service;

import com.example.{project_name.lower()}.dto.{entity_name}DTO;
import com.example.{project_name.lower()}.exception.AlreadyExistsException;
import com.example.{project_name.lower()}.exception.NotFoundException;
import com.example.{project_name.lower()}.model.{entity_name};
import com.example.{project_name.lower()}.model.{entity_name}Mapper;
import com.example.{project_name.lower()}.repository.{entity_name}Repository;
import com.example.{project_name.lower()}.specification.ResultadoSpecifications;
import com.example.{project_name.lower()}.specification.SearchCriteria;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.*;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;

@Service
public class {entity_name}Service {{

    private final {entity_name}Repository {entity_name.lower()}Repository;
    private final {entity_name}Mapper {entity_name.lower()}Mapper;

    @Autowired
    public {entity_name}Service({entity_name}Repository {entity_name.lower()}Repository, {entity_name}Mapper {entity_name.lower()}Mapper) {{
        this.{entity_name.lower()}Repository = {entity_name.lower()}Repository;
        this.{entity_name.lower()}Mapper = {entity_name.lower()}Mapper;
    }}

    public {entity_name}DTO create{entity_name}({entity_name}DTO dto) {{
        if ({entity_name.lower()}Repository.existsById(dto.getId())) {{
            throw new AlreadyExistsException("El {entity_name} con el ID ya existe.");
        }}
        {entity_name} entity = {entity_name.lower()}Mapper.toEntity(dto);
        return {entity_name.lower()}Mapper.toDTO({entity_name.lower()}Repository.save(entity));
    }}

    public {entity_name}DTO get{entity_name}ById(String id) {{
        return {entity_name.lower()}Repository.findById(id)
                .map({entity_name.lower()}Mapper::toDTO)
                .orElseThrow(() -> new NotFoundException("{entity_name} no encontrado"));
    }}

    public {entity_name}DTO update{entity_name}(String id, {entity_name}DTO dto) {{
        {entity_name} entity = {entity_name.lower()}Repository.findById(id)
                .orElseThrow(() -> new NotFoundException("{entity_name} no encontrado"));
        {entity_name.lower()}Mapper.updateEntityFromDTO(dto, entity);
        return {entity_name.lower()}Mapper.toDTO({entity_name.lower()}Repository.save(entity));
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
                .map({entity_name.lower()}Mapper::toDTO);
    }}
}}
'''
    return service_content

# Función para generar el contenido del repository
def generate_repository_content(entity_name, project_name):
    repository_content = f'''package com.example.{project_name.lower()}.repository;

import com.example.{project_name.lower()}.model.{entity_name};
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface {entity_name}Repository extends JpaRepository<{entity_name}, String>, JpaSpecificationExecutor<{entity_name}> {{
}}
'''
    return repository_content

# Función para generar el contenido del DTO
def generate_dto_content(entity_name, attributes, project_name):
    # Solo extraemos attr_name y attr_type, ignorando is_pk (el tercer valor)
    dto_fields = "\n".join([f"    private {attr_type} {attr_name};" for attr_name, attr_type, _ in attributes])
    dto_content = f'''package com.example.{project_name.lower()}.dto;

import lombok.*;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class {entity_name}DTO {{
{dto_fields}
}}
'''
    return dto_content

# Función para generar la clase Mapper con MapStruct
def generate_mapper_content(entity_name, project_name):
    mapper_content = f'''package com.example.{project_name.lower()}.model;

import org.mapstruct.*;
import com.example.{project_name.lower()}.dto.{entity_name}DTO;

@Mapper(componentModel = "spring")
public interface {entity_name}Mapper {{

    {entity_name}DTO toDTO({entity_name} {entity_name.lower()});

    {entity_name} toEntity({entity_name}DTO {entity_name.lower()}DTO);

    @Mapping(target = "id", ignore = true)
    void updateEntityFromDTO({entity_name}DTO {entity_name.lower()}DTO, @MappingTarget {entity_name} {entity_name.lower()});
}}
'''
    return mapper_content

# Función para generar la clase de la entidad (modelo)
def generate_entity_content(entity_name, table_name, attributes, project_name):
    fields = []
    
    for attr_name, attr_type, is_pk in attributes:
        # Añadir anotación @Id solo si el campo es clave primaria
        if is_pk:
            fields.append(f"    @Id")
            fields.append(f"    @Column(nullable = false, unique = true)")
        fields.append(f"    private {attr_type} {attr_name};")
    
    fields_str = "\n".join(fields)

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

{fields_str}
}}
'''
    return entity_content

# Función para generar excepciones NotFound y AlreadyExists
def generate_exceptions_content(entity_name, project_name):
    not_found_exception_content = f'''package com.example.{project_name.lower()}.exception;

public class NotFoundException extends RuntimeException {{
    public NotFoundException(String message) {{
        super(message);
    }}
}}
'''
    already_exists_exception_content = f'''package com.example.{project_name.lower()}.exception;

public class AlreadyExistsException extends RuntimeException {{
    public AlreadyExistsException(String message) {{
        super(message);
    }}
}}
'''
    return not_found_exception_content, already_exists_exception_content

# Función para generar la clase ApplicationMain
def generate_application_main_content(project_name):
    return f'''package com.example.{project_name.lower()};

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class ApplicationMain {{
    public static void main(String[] args) {{
        SpringApplication.run(ApplicationMain.class, args);
    }}
}}
'''

# Función para generar la clase SearchCriteria
def generate_search_criteria(project_name):
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

# Función para generar el archivo application.yml
def generate_application_yml(use_h2):
    if use_h2:
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
    else:
        # Aquí puedes agregar la configuración para otra base de datos o una configuración vacía
        application_yml_content = '''server:
  port: 8080

spring:
  datasource:
    url: jdbc:mysql://localhost:3306/mydb
    driverClassName: com.mysql.cj.jdbc.Driver
    username: root
    password: password
  jpa:
    hibernate:
      ddl-auto: update
    show-sql: true

logging:
  level:
    org.springframework: INFO
    com.example: DEBUG
'''
    return application_yml_content

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
    return resultadosSpecification;

# Generar el proyecto completo
def generate_project():
    project_name = input("Introduce el nombre del proyecto (valor por defecto 'resultado'): ").strip() or "resultado"
    entity_name = input(f"Introduce el nombre de la entidad principal (valor por defecto '{project_name.capitalize()}'): ").strip() or project_name.capitalize()
    table_name = input(f"Introduce el nombre de la tabla para {entity_name} (valor por defecto '{project_name.lower()}s'): ").strip() or f"{project_name.lower()}s"

    attributes = ask_attributes()
    endpoints = ask_endpoints()
    use_h2 = ask_database()
    dependencies = ask_dependencies()

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

    # Generar y guardar el controlador basado en las selecciones de endpoints
    controller_content = generate_controller_content(entity_name, project_name, endpoints)
    with open(os.path.join(packages["controller"], f"{entity_name}Controller.java"), "w") as f:
        f.write(controller_content)

    # Generar y guardar el servicio
    service_content = generate_service_content(entity_name, project_name)
    with open(os.path.join(packages["service"], f"{entity_name}Service.java"), "w") as f:
        f.write(service_content)

    # Generar y guardar el repository
    repository_content = generate_repository_content(entity_name, project_name)
    with open(os.path.join(packages["repository"], f"{entity_name}Repository.java"), "w") as f:
        f.write(repository_content)

    # Generar y guardar el DTO
    dto_content = generate_dto_content(entity_name, attributes, project_name)
    with open(os.path.join(packages["dto"], f"{entity_name}DTO.java"), "w") as f:
        f.write(dto_content)

    # Generar y guardar el mapper
    mapper_content = generate_mapper_content(entity_name, project_name)
    with open(os.path.join(packages["model"], f"{entity_name}Mapper.java"), "w") as f:
        f.write(mapper_content)

    # Generar y guardar la entidad
    entity_content = generate_entity_content(entity_name, table_name, attributes, project_name)
    with open(os.path.join(packages["model"], f"{entity_name}.java"), "w") as f:
        f.write(entity_content)

    # Generar y guardar excepciones
    not_found_exception_content, already_exists_exception_content = generate_exceptions_content(entity_name, project_name)
    with open(os.path.join(packages["exception"], "NotFoundException.java"), "w") as f:
        f.write(not_found_exception_content)
    with open(os.path.join(packages["exception"], "AlreadyExistsException.java"), "w") as f:
        f.write(already_exists_exception_content)

    # Generar y guardar ApplicationMain
    application_main_content = generate_application_main_content(project_name)
    with open(os.path.join(src_main_java, "ApplicationMain.java"), "w") as f:
        f.write(application_main_content)

    # Generar el archivo application.yml
    application_yml_content = generate_application_yml(use_h2)
    with open(os.path.join(src_main_resources, "application.yml"), "w") as f:
        f.write(application_yml_content)

    # Generar el archivo SearchCriteria
    search_criteria_content = generate_search_criteria(project_name)
    with open(os.path.join(packages["specification"], "SearchCriteria.java"), "w") as f:
        f.write(search_criteria_content)
    
     # Generar el archivo ResultadoSpecifications
    resultadosSpecification = generate_specification_content(project_name)
    with open(os.path.join(packages["specification"], "ResultadoSpecifications.java"), "w") as f:
        f.write(resultadosSpecification)

    # Generar el archivo pom.xml
    pom_content = generate_pom_content(project_name, dependencies, use_h2)
    with open(os.path.join(base_dir, "pom.xml"), "w") as f:
        f.write(pom_content)

# Ejecutar el script
generate_project()
