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
        ("org.springframework.boot", "spring-boot-starter-test", "3.1.4", "test"),
        ("org.junit.jupiter", "junit-jupiter-api", "5.8.1", "test"),
        ("org.junit.jupiter", "junit-jupiter-engine", "5.8.1", "test"),
        ("org.mockito", "mockito-core", "3.12.4", "test"),
        ("org.mockito", "mockito-junit-jupiter", "3.12.4", "test"),
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

# Función para preguntar los atributos de la entidad y DTO
def ask_attributes():
    attributes = []
    while True:
        attr_name = input(f"Introduce el nombre del atributo (o presiona Enter para finalizar, valor por defecto 'id'): ").strip() or "id"
        attr_type = input(f"Introduce el tipo del atributo {attr_name} (valor por defecto 'String'): ").strip() or "String"
        is_primary = input(f"¿Es {attr_name} la clave primaria? (S/n, por defecto 'S'): ").strip().lower() or "s"
        attributes.append((attr_name, attr_type, is_primary == "s"))
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

# Función para generar el contenido del test para el servicio
def generate_service_test_content(entity_name, project_name):
    return f'''package com.example.{project_name.lower()}.service;

import com.example.{project_name.lower()}.dto.{entity_name}DTO;
import com.example.{project_name.lower()}.model.{entity_name};
import com.example.{project_name.lower()}.model.{entity_name}Mapper;
import com.example.{project_name.lower()}.repository.{entity_name}Repository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;

import java.util.Arrays;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;

class {entity_name}ServiceTest {{
    @Mock
    private {entity_name}Repository {entity_name.lower()}Repository;

    @Mock
    private {entity_name}Mapper {entity_name.lower()}Mapper;

    @InjectMocks
    private {entity_name}Service {entity_name.lower()}Service;

    private {entity_name}DTO {entity_name.lower()}DTO;
    private {entity_name} {entity_name.lower()};

    @BeforeEach
    void setUp() {{
        MockitoAnnotations.openMocks(this);
        {entity_name.lower()}DTO = new {entity_name}DTO();
        {entity_name.lower()} = new {entity_name}();
    }}

    @Test
    void testCreate{entity_name}() {{
        when({entity_name.lower()}Repository.save(any({entity_name}.class))).thenReturn({entity_name.lower()});
        when({entity_name.lower()}Mapper.toDTO(any({entity_name}.class))).thenReturn({entity_name.lower()}DTO);
        when({entity_name.lower()}Mapper.toEntity(any({entity_name}DTO.class))).thenReturn({entity_name.lower()});

        {entity_name}DTO created = {entity_name.lower()}Service.create{entity_name}({entity_name.lower()}DTO);
        assertNotNull(created);
    }}

    @Test
    void testGet{entity_name}ById() {{
        when({entity_name.lower()}Repository.findById(anyString())).thenReturn(Optional.of({entity_name.lower()}));
        when({entity_name.lower()}Mapper.toDTO(any({entity_name}.class))).thenReturn({entity_name.lower()}DTO);

        {entity_name}DTO dto = {entity_name.lower()}Service.get{entity_name}ById("1");
        assertNotNull(dto);
    }}

    @Test
    void testUpdate{entity_name}() {{
        when({entity_name.lower()}Repository.findById(anyString())).thenReturn(Optional.of({entity_name.lower()}));
        when({entity_name.lower()}Repository.save(any({entity_name}.class))).thenReturn({entity_name.lower()});
        when({entity_name.lower()}Mapper.toDTO(any({entity_name}.class))).thenReturn({entity_name.lower()}DTO);

        {entity_name}DTO updated = {entity_name.lower()}Service.update{entity_name}("1", {entity_name.lower()}DTO);
        assertNotNull(updated);
    }}

    @Test
    void testDelete{entity_name}() {{
        when({entity_name.lower()}Repository.existsById(anyString())).thenReturn(true);
        doNothing().when({entity_name.lower()}Repository).deleteById(anyString());

        assertDoesNotThrow(() -> {entity_name.lower()}Service.delete{entity_name}("1"));
    }}

    @Test
    void testSearch{entity_name}s() {{
        Pageable pageable = PageRequest.of(0, 10);
        Page<{entity_name}> page = new PageImpl<>(
            Arrays.asList({entity_name.lower()}, {entity_name.lower()}),
            pageable, 2
        );

        when({entity_name.lower()}Repository.findAll(any(), any(Pageable.class))).thenReturn(page);

        Page<{entity_name}DTO> result = {entity_name.lower()}Service.search{entity_name}s(null, 0, 10);
        assertEquals(2, result.getTotalElements());
    }}
}}
'''

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
    src_test_java = os.path.join(base_dir, "src", "test", "java", "com", "example", project_name)
    os.makedirs(src_main_java, exist_ok=True)
    os.makedirs(src_main_resources, exist_ok=True)
    os.makedirs(src_test_java, exist_ok=True)

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

    # Generar el archivo pom.xml
    pom_content = generate_pom_content(project_name, dependencies, use_h2)
    with open(os.path.join(base_dir, "pom.xml"), "w") as f:
        f.write(pom_content)

    # Generar los tests unitarios para el servicio
    service_test_content = generate_service_test_content(entity_name, project_name)
    with open(os.path.join(src_test_java, f"{entity_name}ServiceTest.java"), "w") as f:
        f.write(service_test_content)

# Ejecutar el script
generate_project()
