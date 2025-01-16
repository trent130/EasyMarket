import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
  } from "@/components/ui/dialog";
  import { AddProductForm } from "./ProductForm";
  interface AddProductModalProps {
    open: boolean;
    onOpenChange: (open: boolean) => void;
  }
  export const AddProductModal = ({ open, onOpenChange }: AddProductModalProps) => {
    return (
      <Dialog open={open} onOpenChange={onOpenChange}>
        <DialogContent className="sm:max-w-[500px]">
          <DialogHeader>
            <DialogTitle className="text-xl font-light">Add New Product</DialogTitle>
          </DialogHeader>
          <AddProductForm onSuccess={() => onOpenChange(false)} />
        </DialogContent>
      </Dialog>
    );
  };