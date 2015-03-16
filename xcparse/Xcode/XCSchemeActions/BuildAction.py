import xml.etree.ElementTree as xml
from ...Helpers import xcrun_helper
from ..PBX import PBXResolver
from .Base_Action import *
from .BuildActionEntry import *

class BuildAction(Base_Action):
    
    def __init__(self, action_xml):
        self.contents = action_xml;
        if 'parallelizeBuildables' in self.contents.keys():
            self.parallel = self.contents.get('parallelizeBuildables');
        if 'buildImplicitDependencies' in self.contents.keys():
            self.implicit = self.contents.get('buildImplicitDependencies');
        self.children = list(map(lambda entry: BuildActionEntry(entry), list(self.contents.find('./BuildActionEntries'))));
        
    def performAction(self, build_system, container, xcparse_object, scheme_config_settings):
        """
        build_system = xcbuildsystem object - create with `xcbuildsystem()`
        container = xcscheme object - scheme that is having an action performed
        xcparse_object = xcparse object
        scheme_config_settings = dictionary containing any additional environment variables to set
        """
        for child in self.children:
            project_path = xcrun_helper.resolvePathFromLocation(child.target.ReferencedContainer, container[2].path.base_path, container[2].path.base_path);
            project = filter(lambda proj: proj.path.obj_path == project_path, xcparse_object.projects());
            if len(project) > 0:
                project = project[0];
            else:
                project = xcparse_object.project_constructor(project_path);
            
            if USE_XCODE_BUILD == 1:
                xcrun_helper.perform_xcodebuild(project, container[1].name, 'build', scheme_config_settings);
            else:
                self.buildTarget(build_system, project, child.target.BlueprintIdentifier);
        
    def buildTarget(self, build_system, project, target_identifier):
        """
        This method dispatches building a target in a project file.
        
        build_system = xcbuildsystem object
        project = xcodeproj object - taken from BuildAction.performAction()
        target_identifier = string identifier of the object in the xcodeproj file
        """
        target_constructor = PBXResolver(project.objects()[target_identifier]);
        if target_constructor[0] == True:
            target = target_constructor[1](PBXResolver, project.objects()[target_identifier], project, target_identifier);
            print target.name;
            print '========================';
            for dependent in target.dependencies:
                self.buildTarget(build_system, project, dependent.proxy.remoteGlobalIDString);
            for phase in target.buildPhases:
                phase.performPhase(build_system, target);