import { Sidebar, SidebarContent, SidebarFooter, SidebarHeader, SidebarGroup } from "../../src/components/ui/sidebar";


export function AppSidebar (){
    return (
        <Sidebar>
            <SidebarHeader />
            <SidebarContent>
                <SidebarGroup></SidebarGroup>
            </SidebarContent>
            <SidebarFooter />
        </Sidebar>
    );
}