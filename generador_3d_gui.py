import sys
import numpy as np
import os
import tempfile

# Importar CadQuery y PyVista
import cadquery as cq
import pyvista as pv

# Importar componentes de PyQt5
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QPushButton, QFormLayout, QDoubleSpinBox,
                             QFileDialog, QSpinBox, QLabel, QComboBox, QGroupBox)
from PyQt5.QtCore import Qt
from pyvistaqt import QtInteractor

# Establecer el tema de PyVista
pv.set_plot_theme("document")

# --- Clase Principal de la GUI (Adaptada para CadQuery) ---
class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Diseñador de Resonadores (con CadQuery)")
        self.setGeometry(100, 100, 1600, 900)
        
        # Atributos para almacenar las geometrías de CadQuery
        self.resonator_cq = None
        self.inner_object_cq = None
        self.cap_cq = None
        self.cap_with_inner_object_cq = None
        self.equivalent_cylinder_cq = None # Nuevo cilindro

        # --- Configuración de la Interfaz Gráfica ---
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        controls_widget = QWidget()
        controls_layout = QVBoxLayout(controls_widget)
        controls_widget.setMaximumWidth(350)
        
        general_group = QGroupBox("Parámetros del Resonador")
        form_layout = QFormLayout(general_group)
        self.l_input = QDoubleSpinBox(self, value=100.0, maximum=10000.0, singleStep=10.0, suffix=" mm")
        self.d1_input = QDoubleSpinBox(self, value=19.0, maximum=1000.0, singleStep=1.0, suffix=" mm")
        self.thickness_input = QDoubleSpinBox(self, value=2.0, maximum=100.0, singleStep=0.5, suffix=" mm")
        form_layout.addRow("Largo Interno (L):", self.l_input)
        form_layout.addRow("Diámetro Interno (D1):", self.d1_input)
        form_layout.addRow("Espesor de Pared:", self.thickness_input)
        
        inner_tube_group = QGroupBox("Objeto Interno")
        inner_tube_layout = QFormLayout(inner_tube_group)
        self.shape_selector = QComboBox()
        self.shape_selector.addItems(["Elipse", "Estrella", "Polígono"])
        self.ratio_s_input = QDoubleSpinBox(self, value=0.1, maximum=1.0, singleStep=0.05, decimals=3)
        inner_tube_layout.addRow("Forma:", self.shape_selector)
        inner_tube_layout.addRow("Ratio de Área (S2/S1):", self.ratio_s_input)
        
        self.ellipse_group = QGroupBox("Parámetros de Elipse")
        ellipse_layout = QFormLayout(self.ellipse_group)
        self.ratio_ellipse_input = QDoubleSpinBox(self, value=1.5, minimum=1.0, maximum=10.0, singleStep=0.1)
        ellipse_layout.addRow("Ratio Ejes (a/b):", self.ratio_ellipse_input)
        
        self.star_group = QGroupBox("Parámetros de Estrella")
        star_layout = QFormLayout(self.star_group)
        self.star_points_input = QSpinBox(self, value=5, minimum=3, maximum=50)
        self.star_ratio_input = QDoubleSpinBox(self, value=0.5, minimum=0.1, maximum=0.99, singleStep=0.05)
        star_layout.addRow("Puntas:", self.star_points_input)
        star_layout.addRow("Ratio Radios (r_in/r_out):", self.star_ratio_input)
        
        self.polygon_group = QGroupBox("Parámetros de Polígono")
        polygon_layout = QFormLayout(self.polygon_group)
        self.polygon_sides_input = QSpinBox(self, value=6, minimum=3, maximum=50)
        polygon_layout.addRow("Número de Lados:", self.polygon_sides_input)
        
        self.cap_group = QGroupBox("Parámetros de la Tapa")
        cap_layout = QFormLayout(self.cap_group)
        self.cap_wall_thickness_input = QDoubleSpinBox(self, value=2.0, minimum=0.5, maximum=100.0, singleStep=0.1, suffix=" mm")
        self.cap_cavity_depth_input = QDoubleSpinBox(self, value=5.0, minimum=1.0, maximum=100.0, singleStep=0.5, suffix=" mm")
        cap_layout.addRow("Espesor de Pared:", self.cap_wall_thickness_input)
        cap_layout.addRow("Profundidad de Cavidad:", self.cap_cavity_depth_input)

        verification_group = QGroupBox("Análisis de Sección Transversal")
        verification_layout = QFormLayout(verification_group)
        self.area_resonator_label = QLabel("N/A mm²")
        self.area_object_label = QLabel("N/A mm²")
        self.area_net_material_label = QLabel("N/A mm²")
        self.area_equivalent_material_val_label = QLabel("N/A mm²")
        verification_layout.addRow("Área Material Resonador:", self.area_resonator_label)
        verification_layout.addRow("Área Obj. Interno:", self.area_object_label)
        verification_layout.addRow("Área Material Neta:", self.area_net_material_label)
        verification_layout.addRow("Área Material Cyl. Equiv.:", self.area_equivalent_material_val_label)


        self.update_button = QPushButton("Actualizar Vista 3D")
        self.save_button = QPushButton("Guardar Archivos STL...")

        controls_layout.addWidget(general_group)
        controls_layout.addWidget(inner_tube_group)
        controls_layout.addWidget(self.ellipse_group)
        controls_layout.addWidget(self.star_group)
        controls_layout.addWidget(self.polygon_group)
        controls_layout.addWidget(self.cap_group)
        controls_layout.addWidget(verification_group)
        controls_layout.addStretch()
        controls_layout.addWidget(self.update_button)
        controls_layout.addWidget(self.save_button)
        
        self.plotter = QtInteractor(self)
        main_layout.addWidget(controls_widget)
        main_layout.addWidget(self.plotter.interactor, 1)
        
        self.shape_selector.currentIndexChanged.connect(self._on_shape_change)
        self.update_button.clicked.connect(self.update_plot)
        self.save_button.clicked.connect(self.save_stl)
        
        self._on_shape_change()
        self.update_plot()

    def _on_shape_change(self):
        shape = self.shape_selector.currentText()
        self.ellipse_group.setVisible(shape == "Elipse")
        self.star_group.setVisible(shape == "Estrella")
        self.polygon_group.setVisible(shape == "Polígono")

    def _generate_geometry_cq(self):
        self.resonator_cq = self.inner_object_cq = self.cap_cq = self.cap_with_inner_object_cq = self.equivalent_cylinder_cq = None
        L = self.l_input.value()
        D1 = self.d1_input.value()
        THICKNESS = self.thickness_input.value()
        cap_wall_thickness = self.cap_wall_thickness_input.value()
        cap_cavity_depth = self.cap_cavity_depth_input.value()

        if D1 <= 0 or L <= 0: return False

        R1 = D1 / 2.0
        R2 = R1 + THICKNESS
        S1 = np.pi * R1**2
        S2_target = self.ratio_s_input.value() * S1
        shape = self.shape_selector.currentText()
        
        self.resonator_cq = cq.Workplane("XY").circle(R2).circle(R1).extrude(L)

        profile_points = []
        try:
            if shape == "Elipse":
                ratio_ab = self.ratio_ellipse_input.value()
                a = np.sqrt(S2_target * ratio_ab / np.pi) if S2_target > 0 else 0
                b = a / ratio_ab if ratio_ab > 0 else 0
                theta = np.linspace(0, 2 * np.pi, 200, endpoint=True)
                profile_points = list(zip(a * np.cos(theta), b * np.sin(theta)))
            elif shape == "Estrella":
                n_tips, ratio_r = self.star_points_input.value(), self.star_ratio_input.value()
                area_factor = n_tips * np.sin(np.pi / n_tips) * np.cos(np.pi / n_tips) * (1 - ratio_r**2)
                r_outer = np.sqrt(S2_target / area_factor) if area_factor > 0 else 0
                r_inner = r_outer * ratio_r
                theta = np.linspace(0, 2 * np.pi, 2 * n_tips, endpoint=False)
                radii = np.tile([r_outer, r_inner], n_tips)
                profile_points = list(zip(radii * np.cos(theta), radii * np.sin(theta)))
            elif shape == "Polígono":
                n_sides = self.polygon_sides_input.value()
                area_factor = 0.5 * n_sides * np.sin(2 * np.pi / n_sides)
                radius = np.sqrt(S2_target / area_factor) if area_factor > 0 else 0
                theta = np.linspace(0, 2 * np.pi, n_sides, endpoint=True)
                profile_points = list(zip(radius * np.cos(theta), radius * np.sin(theta)))

            if profile_points:
                self.inner_object_cq = cq.Workplane("XY").polyline(profile_points).close().extrude(L)
        except (ValueError, ZeroDivisionError):
            self.inner_object_cq = None

        cap_inner_radius = R2
        cap_outer_radius = cap_inner_radius + cap_wall_thickness
        cap_total_height = cap_cavity_depth + cap_wall_thickness
        cap_base = cq.Workplane("XY").circle(cap_outer_radius).extrude(cap_total_height)
        cavity_tool = cq.Workplane("XY").workplane(offset=cap_total_height).circle(cap_inner_radius).extrude(-cap_cavity_depth)
        self.cap_cq = cap_base.cut(cavity_tool)
        
        if self.cap_cq and self.inner_object_cq:
            moved_inner_object = self.inner_object_cq.translate((0, 0, cap_wall_thickness))
            self.cap_with_inner_object_cq = self.cap_cq.union(moved_inner_object)
        
        area_material_resonador = np.pi * (R2**2 - R1**2)
        area_objeto = S2_target if self.inner_object_cq else 0.0
        area_neta_material = area_material_resonador - area_objeto
        
        self.area_resonator_label.setText(f"{area_material_resonador:.2f} mm²")
        self.area_object_label.setText(f"{area_objeto:.2f} mm²")
        self.area_net_material_label.setText(f"{area_neta_material:.2f} mm²")

        R1_new = 0
        if area_neta_material > 1e-9:
            new_hole_area = area_neta_material
            R1_new = np.sqrt(new_hole_area / np.pi)
            R2_new = R2

            if R1_new < R2_new:
                self.equivalent_cylinder_cq = cq.Workplane("XY").circle(R2_new).circle(R1_new).extrude(L)
                area_mat_eq_cyl = np.pi * (R2_new**2 - R1_new**2)
                self.area_equivalent_material_val_label.setText(f"{area_mat_eq_cyl:.2f} mm²")
            else:
                self.area_equivalent_material_val_label.setText("Error: R_in > R_out")
                self.equivalent_cylinder_cq = None
        else:
            self.area_net_material_label.setText("Error: Obj. muy grande")
            self.area_equivalent_material_val_label.setText("N/A")
            self.equivalent_cylinder_cq = None

        return True

    def update_plot(self):
        success = self._generate_geometry_cq()
        self.plotter.clear()
        if not success:
            self.plotter.reset_camera()
            return

        def display_cq_object(obj, **kwargs):
            if obj is None: return
            with tempfile.NamedTemporaryFile(suffix=".stl", delete=False) as temp:
                temp_filename = temp.name
            try:
                cq.exporters.export(obj, temp_filename)
                mesh = pv.read(temp_filename)
                self.plotter.add_mesh(mesh, **kwargs)
            finally:
                if os.path.exists(temp_filename):
                    os.remove(temp_filename)

        display_cq_object(self.resonator_cq, color='lightgrey', show_edges=True, opacity=0.3)
        if self.inner_object_cq:
            display_cq_object(self.inner_object_cq, color='cornflowerblue', show_edges=True)
        
        cap_outer_radius = (self.d1_input.value() / 2.0) + self.thickness_input.value() + self.cap_wall_thickness_input.value()
        translation_dist = cap_outer_radius * 2.5
        
        if self.cap_with_inner_object_cq:
            display_assembly = self.cap_with_inner_object_cq.translate((-translation_dist * 1.5, 0, 0))
            display_cq_object(display_assembly, color='goldenrod', show_edges=True)

        if self.equivalent_cylinder_cq:
            display_equivalent = self.equivalent_cylinder_cq.translate((translation_dist, 0, 0))
            display_cq_object(display_equivalent, color='mediumseagreen', show_edges=True)

        if self.cap_cq:
            display_cap = self.cap_cq.rotate((0, 0, 0), (1, 0, 0), 180).translate((translation_dist * 2, 0, 0))
            display_cq_object(display_cap, color='tomato', show_edges=True)

        self.plotter.add_axes()
        self.plotter.reset_camera()

    def save_stl(self):
        if not self.resonator_cq: 
            print("No hay geometría para guardar. Presiona 'Actualizar Vista 3D' primero.")
            return
            
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar Archivos STL", "resonador_ensamble.stl", "STL Files (*.stl)")
        if not filename:
            print("Guardado cancelado por el usuario.")
            return
        
        base, _ = os.path.splitext(filename)
        print("-" * 20)
        print(f"Directorio base para guardado: {os.path.dirname(filename)}")
        
        try:
            cq.exporters.export(self.resonator_cq, base + "_resonador_hueco.stl")
            print(f"OK: Resonador hueco guardado.")
            
            if self.cap_cq:
                cq.exporters.export(self.cap_cq, base + "_tapa_sola.stl")
                print(f"OK: Tapa sola (sin invertir) guardada.")

            if self.inner_object_cq:
                cq.exporters.export(self.inner_object_cq, base + "_objeto_interno_solo.stl")
                print(f"OK: Objeto interno solo guardado.")
            
            if self.cap_with_inner_object_cq:
                cq.exporters.export(self.cap_with_inner_object_cq, base + "_tapa_con_objeto_interno.stl")
                print(f"OK: Ensamble de tapa con objeto interno guardado.")

            if self.equivalent_cylinder_cq:
                cq.exporters.export(self.equivalent_cylinder_cq, base + "_cilindro_equivalente.stl")
                print(f"OK: Cilindro equivalente guardado.")
            
            print("-" * 20)
        except Exception as e: 
            print(f"ERROR: No se pudieron guardar los archivos: {e}")


if __name__ == '__main__':
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    window = App()
    window.show()
    sys.exit(app.exec_())
